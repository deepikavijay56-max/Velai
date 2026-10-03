from typing import List
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.models.gig import Gig, GigStatus
from app.models.application import Application, ApplicationStatus
from app.models.contract import Contract, ContractStatus
from app.schemas.application import ApplicationCreate, ApplicationRead
from app.schemas.contract import ContractRead

router = APIRouter(tags=["Applications"])


@router.post("/gigs/{gig_id}/apply", response_model=ApplicationRead, summary="Apply for an open gig")
async def apply_to_gig(
    gig_id: str,
    payload: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only students can apply
    if current_user.role != UserRole.STUDENT and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can apply to gigs",
        )

    # Fetch gig
    stmt = select(Gig).where(Gig.id == gig_id)
    res = await db.execute(stmt)
    gig = res.scalar_one_or_none()
    if not gig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gig not found")

    if gig.status != GigStatus.Open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot apply: gig is in '{gig.status.value}' state, must be 'Open'",
        )

    if gig.poster_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot apply to your own gig",
        )

    # Check for existing application
    app_stmt = select(Application).where(
        Application.gig_id == gig_id,
        Application.user_id == current_user.id,
    )
    existing_app = (await db.execute(app_stmt)).scalar_one_or_none()
    if existing_app:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this gig",
        )

    app_record = Application(
        gig_id=gig_id,
        user_id=current_user.id,
        pitch=payload.pitch.strip(),
        sample_url=payload.sample_url,
        proposed_price=payload.proposed_price,
        proposed_days=payload.proposed_days,
        status=ApplicationStatus.PENDING,
    )
    db.add(app_record)
    await db.commit()
    await db.refresh(app_record)

    # Re-fetch with user
    full_stmt = select(Application).where(Application.id == app_record.id).options(selectinload(Application.user))
    full_app = (await db.execute(full_stmt)).scalar_one()
    return full_app


@router.get("/gigs/{gig_id}/applications", response_model=List[ApplicationRead], summary="View applicants for a gig")
async def list_gig_applications(
    gig_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Gig).where(Gig.id == gig_id)
    gig = (await db.execute(stmt)).scalar_one_or_none()
    if not gig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gig not found")

    if gig.poster_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the gig poster can view applicants",
        )

    app_stmt = (
        select(Application)
        .where(Application.gig_id == gig_id)
        .options(selectinload(Application.user).selectinload(User.skills))
        .order_by(Application.created_at.desc())
    )
    apps = (await db.execute(app_stmt)).scalars().all()
    return apps


@router.post("/applications/{application_id}/accept", response_model=ContractRead, summary="Poster accepts an applicant")
async def accept_application(
    application_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Fetch application with gig
    app_stmt = (
        select(Application)
        .where(Application.id == application_id)
        .options(selectinload(Application.gig), selectinload(Application.user))
    )
    app_res = await db.execute(app_stmt)
    application = app_res.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    gig = application.gig
    if gig.poster_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the poster can accept applicants")

    if gig.status != GigStatus.Open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot accept applicant: gig is currently '{gig.status.value}'",
        )

    # Check if a contract already exists
    existing_contract_stmt = select(Contract).where(Contract.gig_id == gig.id)
    existing_contract = (await db.execute(existing_contract_stmt)).scalar_one_or_none()
    if existing_contract:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contract already exists for this gig")

    now = datetime.now(timezone.utc)
    agreed_deadline = now + timedelta(days=application.proposed_days)

    # Create Contract with poster's acceptance timestamp
    contract = Contract(
        college_id=gig.college_id,
        gig_id=gig.id,
        poster_id=gig.poster_id,
        doer_id=application.user_id,
        agreed_price=application.proposed_price,
        agreed_deadline=agreed_deadline,
        agreed_revisions=gig.revisions,
        revisions_used=0,
        confirmed_by_poster_at=now,
        confirmed_by_doer_at=None,
        status=ContractStatus.PENDING_CONFIRMATION,
    )
    db.add(contract)

    # Update application statuses
    application.status = ApplicationStatus.ACCEPTED

    # Reject other applications
    other_apps_stmt = select(Application).where(
        Application.gig_id == gig.id,
        Application.id != application.id,
    )
    other_apps = (await db.execute(other_apps_stmt)).scalars().all()
    for o_app in other_apps:
        o_app.status = ApplicationStatus.REJECTED

    await db.commit()
    await db.refresh(contract)

    # Load contract details
    c_stmt = (
        select(Contract)
        .where(Contract.id == contract.id)
        .options(
            selectinload(Contract.poster),
            selectinload(Contract.doer),
            selectinload(Contract.deliverables),
            selectinload(Contract.payment),
            selectinload(Contract.gig),
        )
    )
    full_contract = (await db.execute(c_stmt)).scalar_one()
    return full_contract
