import logging
from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_otp,
    validate_college_email,
)
from app.models.user import User, UserRole, UserSkill, OTPVerification
from app.schemas.auth import (
    OTPRequest,
    OTPVerify,
    TokenResponse,
    UserRead,
    UserUpdate,
    UserSkillCreate,
    UserSkillRead,
)
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication & Profile"])


@router.post("/request-otp", summary="Request login OTP for college email")
async def request_otp(
    payload: OTPRequest,
    db: AsyncSession = Depends(get_db),
):
    email = payload.email.lower().strip()

    # Verify campus domain
    if not validate_college_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration is restricted to college emails ending in '@{settings.COLLEGE_EMAIL_DOMAIN}'",
        )

    otp_code = generate_otp(6)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    # Invalidate previous OTPs for this email
    await db.execute(delete(OTPVerification).where(OTPVerification.email == email))

    otp_record = OTPVerification(
        email=email,
        otp_code=otp_code,
        expires_at=expires_at,
        is_used=False,
    )
    db.add(otp_record)
    await db.commit()

    if settings.DEV_MODE:
        logger.info("Generated development OTP for %s: %s", email, otp_code)

    return {
        "message": f"Verification code sent to {email}",
        "email": email,
        "dev_mock_otp": otp_code if settings.DEV_MODE else None,
    }


@router.post("/verify-otp", response_model=TokenResponse, summary="Verify OTP and return JWT tokens")
async def verify_otp(
    payload: OTPVerify,
    db: AsyncSession = Depends(get_db),
):
    email = payload.email.lower().strip()
    now = datetime.now(timezone.utc)

    # Query OTP record
    stmt = (
        select(OTPVerification)
        .where(
            OTPVerification.email == email,
            OTPVerification.otp_code == payload.otp_code.strip(),
            OTPVerification.is_used == False,
        )
        .order_by(OTPVerification.created_at.desc())
    )
    result = await db.execute(stmt)
    otp_record = result.scalars().first()

    # Allow a configured development OTP only when development mode is enabled.
    is_valid_dev_otp = (
        settings.DEV_MODE
        and settings.DEV_OTP_CODE is not None
        and payload.otp_code.strip() == settings.DEV_OTP_CODE
    )

    if not otp_record and not is_valid_dev_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        )

    if otp_record:
        # Check expiry
        record_exp = otp_record.expires_at
        if record_exp.tzinfo is None:
            record_exp = record_exp.replace(tzinfo=timezone.utc)
        if record_exp < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired. Please request a new one.",
            )
        otp_record.is_used = True
        await db.commit()

    # Check if user already exists
    user_stmt = select(User).where(User.college_email == email).options(selectinload(User.skills))
    user_res = await db.execute(user_stmt)
    user = user_res.scalar_one_or_none()

    if not user:
        # Determine initial role: check if admin email or staff
        role = UserRole.STUDENT
        if email == settings.ADMIN_EMAIL:
            role = UserRole.ADMIN
        elif payload.role and payload.role.lower() in [r.value for r in UserRole]:
            role = UserRole(payload.role.lower())

        user = User(
            college_id=settings.COLLEGE_ID,
            college_email=email,
            name=payload.name or email.split("@")[0].replace(".", " ").title(),
            department=payload.department or "General",
            year=payload.year or 1,
            role=role,
            reputation=5.0,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Issue JWT tokens
    access_token = create_access_token(
        subject=user.id,
        role=user.role.value,
        college_id=user.college_id,
    )
    refresh_token = create_refresh_token(subject=user.id)

    # Ensure skills loaded
    await db.refresh(user, attribute_names=["skills"])

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserRead.model_validate(user),
    )


@router.get("/me", response_model=UserRead, summary="Get current logged in user profile")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserRead, summary="Update user profile")
async def update_me(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.name is not None:
        current_user.name = payload.name
    if payload.department is not None:
        current_user.department = payload.department
    if payload.year is not None:
        current_user.year = payload.year
    if payload.availability is not None:
        current_user.availability = payload.availability

    await db.commit()
    await db.refresh(current_user, attribute_names=["skills"])
    return current_user


@router.put("/me/skills", response_model=List[UserSkillRead], summary="Update student skills and sample links")
async def update_my_skills(
    skills_in: List[UserSkillCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Clear existing skills
    await db.execute(delete(UserSkill).where(UserSkill.user_id == current_user.id))

    new_skills = [
        UserSkill(
            user_id=current_user.id,
            skill_name=s.skill_name.strip(),
            level=s.level,
            sample_links=s.sample_links[:3],  # enforce up to 3 links
        )
        for s in skills_in
    ]
    db.add_all(new_skills)
    await db.commit()

    stmt = select(UserSkill).where(UserSkill.user_id == current_user.id)
    res = await db.execute(stmt)
    return res.scalars().all()
