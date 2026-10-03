from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.contract import Contract, ContractStatus
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewRead

router = APIRouter(tags=["Ratings & Reviews"])


@router.post("/contracts/{contract_id}/review", response_model=ReviewRead, summary="Submit a rating and review for a completed gig")
async def create_review(
    contract_id: str,
    payload: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Contract).where(Contract.id == contract_id)
    contract = (await db.execute(stmt)).scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    if contract.status != ContractStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviews can only be submitted after a gig is completed",
        )

    is_poster = current_user.id == contract.poster_id
    is_doer = current_user.id == contract.doer_id
    if not is_poster and not is_doer and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only contract participants can leave reviews")

    reviewee_id = contract.doer_id if is_poster else contract.poster_id

    # Check if already reviewed by this user
    r_check = select(Review).where(
        Review.contract_id == contract_id,
        Review.reviewer_id == current_user.id,
    )
    existing_rev = (await db.execute(r_check)).scalar_one_or_none()
    if existing_rev:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted a review for this contract",
        )

    review = Review(
        contract_id=contract_id,
        reviewer_id=current_user.id,
        reviewee_id=reviewee_id,
        rating=payload.rating,
        comment=payload.comment,
        tags=payload.tags,
    )
    db.add(review)

    # Update reviewee's reputation score
    u_stmt = select(User).where(User.id == reviewee_id)
    reviewee = (await db.execute(u_stmt)).scalar_one_or_none()
    if reviewee:
        all_rev_stmt = select(Review.rating).where(Review.reviewee_id == reviewee_id)
        all_ratings = (await db.execute(all_rev_stmt)).scalars().all()
        ratings_list = list(all_ratings) + [payload.rating]
        reviewee.reputation = round(sum(ratings_list) / len(ratings_list), 2)

    await db.commit()
    await db.refresh(review)
    return review


@router.get("/users/{user_id}/reviews", response_model=List[ReviewRead], summary="Get all reviews received by a user")
async def list_user_reviews(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Review)
        .where(Review.reviewee_id == user_id)
        .order_by(Review.created_at.desc())
    )
    res = await db.execute(stmt)
    return res.scalars().all()
