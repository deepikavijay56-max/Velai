from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import User, UserRole
from app.models.organization import Organization, OrgVerificationStatus
from app.models.gig import Gig, GigStatus
from app.models.contract import Contract
from app.schemas.organization import OrgRead
from app.schemas.gig import GigRead
from app.api.v1.gigs import format_gig_read

router = APIRouter(prefix="/admin", tags=["Admin Portal"])


@router.get("/orgs", response_model=List[OrgRead], summary="List organizations for admin review")
async def list_orgs_for_admin(
    status_filter: Optional[OrgVerificationStatus] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    stmt = select(Organization).order_by(Organization.created_at.desc())
    if status_filter:
        stmt = stmt.where(Organization.verified_status == status_filter)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/orgs/{org_id}/approve", response_model=OrgRead, summary="Approve an organization")
async def approve_organization(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    stmt = select(Organization).where(Organization.id == org_id)
    res = await db.execute(stmt)
    org = res.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    org.verified_status = OrgVerificationStatus.APPROVED
    await db.commit()
    await db.refresh(org)
    return org


@router.post("/orgs/{org_id}/reject", response_model=OrgRead, summary="Reject an organization")
async def reject_organization(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    stmt = select(Organization).where(Organization.id == org_id)
    res = await db.execute(stmt)
    org = res.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    org.verified_status = OrgVerificationStatus.REJECTED
    await db.commit()
    await db.refresh(org)
    return org


@router.get("/moderation", response_model=List[GigRead], summary="List gigs flagged for academic dishonesty")
async def list_moderation_queue(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    stmt = (
        select(Gig)
        .where(Gig.is_flagged_academic == True)
        .options(
            selectinload(Gig.skills),
            selectinload(Gig.poster),
            selectinload(Gig.organization),
        )
        .order_by(Gig.created_at.desc())
    )
    res = await db.execute(stmt)
    gigs = res.scalars().all()
    return [format_gig_read(g) for g in gigs]


@router.post("/moderation/{gig_id}/resolve", response_model=GigRead, summary="Resolve flagged gig (approve or cancel)")
async def resolve_moderation(
    gig_id: str,
    action: str,  # "approve" or "cancel"
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    stmt = (
        select(Gig)
        .where(Gig.id == gig_id)
        .options(
            selectinload(Gig.skills),
            selectinload(Gig.poster),
            selectinload(Gig.organization),
        )
    )
    res = await db.execute(stmt)
    gig = res.scalar_one_or_none()
    if not gig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gig not found")

    if action == "approve":
        gig.is_flagged_academic = False
        gig.flag_reason = None
    elif action == "cancel":
        gig.status = GigStatus.Cancelled
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Action must be 'approve' or 'cancel'")

    await db.commit()
    await db.refresh(gig)
    return format_gig_read(gig)


@router.get("/stats", summary="Admin high-level overview")
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user_count = (await db.execute(select(func.count(User.id)))).scalar_one() or 0
    gig_count = (await db.execute(select(func.count(Gig.id)))).scalar_one() or 0
    contract_count = (await db.execute(select(func.count(Contract.id)))).scalar_one() or 0
    flagged_count = (await db.execute(select(func.count(Gig.id)).where(Gig.is_flagged_academic == True))).scalar_one() or 0
    pending_orgs = (
        await db.execute(
            select(func.count(Organization.id)).where(Organization.verified_status == OrgVerificationStatus.PENDING)
        )
    ).scalar_one() or 0

    return {
        "total_users": user_count,
        "total_gigs": gig_count,
        "total_contracts": contract_count,
        "flagged_academic_gigs": flagged_count,
        "pending_org_verifications": pending_orgs,
    }
