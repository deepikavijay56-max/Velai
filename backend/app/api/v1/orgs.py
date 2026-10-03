from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgType, OrgVerificationStatus
from app.schemas.organization import OrgCreate, OrgRead

router = APIRouter(prefix="/orgs", tags=["Organizations"])


@router.post("", response_model=OrgRead, summary="Register a club, department, or business")
async def create_organization(
    payload: OrgCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Rule: Businesses must be admin-approved before posting; Clubs & Departments are active
    verified_status = (
        OrgVerificationStatus.PENDING
        if payload.type == OrgType.BUSINESS
        else OrgVerificationStatus.APPROVED
    )

    org = Organization(
        college_id=current_user.college_id,
        name=payload.name.strip(),
        type=payload.type,
        description=payload.description,
        verified_status=verified_status,
        owner_id=current_user.id,
        logo_url=payload.logo_url,
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)

    # Add owner as org member
    member = OrgMember(
        org_id=org.id,
        user_id=current_user.id,
        role="owner",
    )
    db.add(member)
    await db.commit()

    return org


@router.get("", response_model=List[OrgRead], summary="List campus organizations")
async def list_organizations(
    org_type: Optional[OrgType] = None,
    verified_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    college_id = current_user.college_id if current_user else settings.COLLEGE_ID
    stmt = select(Organization).where(Organization.college_id == college_id)
    if verified_only:
        stmt = stmt.where(Organization.verified_status == OrgVerificationStatus.APPROVED)
    if org_type:
        stmt = stmt.where(Organization.type == org_type)

    stmt = stmt.order_by(Organization.name.asc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{org_id}", response_model=OrgRead, summary="Get organization details")
async def get_organization(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    stmt = select(Organization).where(Organization.id == org_id)
    res = await db.execute(stmt)
    org = res.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org
