from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_user_optional
from app.models.user import User, UserSkill
from app.models.organization import Organization, OrgVerificationStatus
from app.models.gig import Gig, GigSkill
from app.models.application import Application
from app.core.state_machine import GigStatus, check_valid_transition
from app.core.moderation import scan_for_academic_dishonesty
from app.schemas.gig import GigCreate, GigUpdate, GigRead

router = APIRouter(prefix="/gigs", tags=["Gigs"])


def format_gig_read(gig: Gig, app_count: int = 0) -> GigRead:
    return GigRead(
        id=gig.id,
        college_id=gig.college_id,
        org_id=gig.org_id,
        poster_id=gig.poster_id,
        title=gig.title,
        category=gig.category,
        description=gig.description,
        deliverables=gig.deliverables or [],
        budget_min=gig.budget_min,
        budget_max=gig.budget_max,
        deadline=gig.deadline,
        revisions=gig.revisions,
        status=gig.status,
        is_flagged_academic=gig.is_flagged_academic,
        flag_reason=gig.flag_reason,
        skills=[s.skill_name for s in (gig.skills or [])],
        poster=gig.poster,
        organization=gig.organization,
        applications_count=app_count,
        created_at=gig.created_at,
        updated_at=gig.updated_at,
    )


@router.post("", response_model=GigRead, summary="Post a new gig")
async def create_gig(
    payload: GigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # If posting under an organization, ensure user has rights and org is verified
    if payload.org_id:
        org_stmt = select(Organization).where(Organization.id == payload.org_id)
        org_res = await db.execute(org_stmt)
        org = org_res.scalar_one_or_none()
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        if org.verified_status != OrgVerificationStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization must be verified before posting gigs",
            )

    # Trust & Safety: Academic Dishonesty Keyword Scanner
    full_text = f"{payload.title} {payload.description}"
    is_flagged, matched_terms = scan_for_academic_dishonesty(full_text)
    flag_reason = f"Contains restricted academic terms: {', '.join(matched_terms)}" if is_flagged else None

    # By default, published directly to Open unless flagged for review
    initial_status = GigStatus.Open

    gig = Gig(
        college_id=current_user.college_id,
        org_id=payload.org_id,
        poster_id=current_user.id,
        title=payload.title.strip(),
        category=payload.category.strip(),
        description=payload.description.strip(),
        deliverables=payload.deliverables,
        budget_min=payload.budget_min,
        budget_max=payload.budget_max,
        deadline=payload.deadline,
        revisions=payload.revisions,
        status=initial_status,
        is_flagged_academic=is_flagged,
        flag_reason=flag_reason,
    )
    db.add(gig)
    await db.commit()
    await db.refresh(gig)

    # Attach skills
    if payload.skills:
        for s_name in payload.skills:
            clean_name = s_name.strip()
            if clean_name:
                db.add(GigSkill(gig_id=gig.id, skill_name=clean_name))
        await db.commit()

    # Re-fetch full gig with relations
    stmt = (
        select(Gig)
        .where(Gig.id == gig.id)
        .options(
            selectinload(Gig.skills),
            selectinload(Gig.poster),
            selectinload(Gig.organization),
        )
    )
    res = await db.execute(stmt)
    full_gig = res.scalar_one()

    return format_gig_read(full_gig, app_count=0)


@router.get("", response_model=List[GigRead], summary="Browse campus gigs with filters")
async def list_gigs(
    category: Optional[str] = None,
    min_budget: Optional[int] = None,
    max_budget: Optional[int] = None,
    status_filter: Optional[GigStatus] = Query(GigStatus.Open, alias="status"),
    matches_my_skills: bool = Query(False, description="Filter for gigs matching student skills"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    college_id = current_user.college_id if current_user else settings.COLLEGE_ID
    stmt = (
        select(Gig)
        .where(Gig.college_id == college_id)
        .options(
            selectinload(Gig.skills),
            selectinload(Gig.poster),
            selectinload(Gig.organization),
        )
    )

    if status_filter:
        stmt = stmt.where(Gig.status == status_filter)

    # Hide unreviewed academic dishonesty violations from the public browse feed
    stmt = stmt.where(Gig.is_flagged_academic == False)

    if category:
        stmt = stmt.where(Gig.category.ilike(f"%{category}%"))
    if min_budget:
        stmt = stmt.where(Gig.budget_max >= min_budget)
    if max_budget:
        stmt = stmt.where(Gig.budget_min <= max_budget)

    # Skills matching filter
    if matches_my_skills:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to filter gigs matching your profile skills",
            )
        user_skills_stmt = select(UserSkill.skill_name).where(UserSkill.user_id == current_user.id)
        u_res = await db.execute(user_skills_stmt)
        user_skill_names = [s.lower() for s in u_res.scalars().all()]
        if user_skill_names:
            stmt = stmt.join(Gig.skills).where(
                func.lower(GigSkill.skill_name).in_(user_skill_names)
            ).distinct()
        else:
            return []

    stmt = stmt.order_by(Gig.created_at.desc())
    result = await db.execute(stmt)
    gigs = result.scalars().all()

    # Get application counts
    gig_ids = [g.id for g in gigs]
    app_counts: dict = {}
    if gig_ids:
        count_stmt = (
            select(Application.gig_id, func.count(Application.id))
            .where(Application.gig_id.in_(gig_ids))
            .group_by(Application.gig_id)
        )
        c_res = await db.execute(count_stmt)
        app_counts = dict(c_res.all())

    return [format_gig_read(g, app_counts.get(g.id, 0)) for g in gigs]


@router.get("/{gig_id}", response_model=GigRead, summary="Get details for a specific gig")
async def get_gig(
    gig_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
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

    count_stmt = select(func.count(Application.id)).where(Application.gig_id == gig.id)
    c_res = await db.execute(count_stmt)
    app_count = c_res.scalar_one() or 0

    return format_gig_read(gig, app_count)


@router.patch("/{gig_id}", response_model=GigRead, summary="Update gig specifications before it starts")
async def update_gig(
    gig_id: str,
    payload: GigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
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

    if gig.poster_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the poster can modify this gig")

    if gig.status not in (GigStatus.Draft, GigStatus.Open):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot edit gig in status '{gig.status.value}'",
        )

    if payload.title is not None:
        gig.title = payload.title.strip()
    if payload.category is not None:
        gig.category = payload.category.strip()
    if payload.description is not None:
        gig.description = payload.description.strip()
    if payload.deliverables is not None:
        gig.deliverables = payload.deliverables
    if payload.budget_min is not None:
        gig.budget_min = payload.budget_min
    if payload.budget_max is not None:
        gig.budget_max = payload.budget_max
    if payload.deadline is not None:
        gig.deadline = payload.deadline
    if payload.revisions is not None:
        gig.revisions = payload.revisions

    # Re-check moderation on title/description update
    full_text = f"{gig.title} {gig.description}"
    is_flagged, matched_terms = scan_for_academic_dishonesty(full_text)
    gig.is_flagged_academic = is_flagged
    gig.flag_reason = f"Contains restricted academic terms: {', '.join(matched_terms)}" if is_flagged else None

    await db.commit()
    await db.refresh(gig)
    return format_gig_read(gig)


@router.post("/{gig_id}/cancel", response_model=GigRead, summary="Cancel an open gig")
async def cancel_gig(
    gig_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
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

    if gig.poster_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the poster can cancel this gig")

    # Enforce state machine transition
    check_valid_transition(gig.status, GigStatus.Cancelled)

    gig.status = GigStatus.Cancelled
    await db.commit()
    await db.refresh(gig)
    return format_gig_read(gig)
