from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.gig import Gig, GigStatus
from app.models.contract import Contract, ContractStatus
from app.core.state_machine import check_valid_transition
from app.schemas.contract import ContractRead

router = APIRouter(prefix="/contracts", tags=["Contracts & Agreements"])


@router.get("/{contract_id}", response_model=ContractRead, summary="Get contract agreement details")
async def get_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Contract)
        .where(Contract.id == contract_id)
        .options(
            selectinload(Contract.poster),
            selectinload(Contract.doer),
            selectinload(Contract.deliverables),
            selectinload(Contract.payment),
            selectinload(Contract.gig),
        )
    )
    res = await db.execute(stmt)
    contract = res.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    if (
        current_user.id != contract.poster_id
        and current_user.id != contract.doer_id
        and current_user.role != "admin"
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return contract


@router.get("/by-gig/{gig_id}", response_model=ContractRead, summary="Get contract by gig ID")
async def get_contract_by_gig(
    gig_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Contract)
        .where(Contract.gig_id == gig_id)
        .options(
            selectinload(Contract.poster),
            selectinload(Contract.doer),
            selectinload(Contract.deliverables),
            selectinload(Contract.payment),
            selectinload(Contract.gig),
        )
    )
    res = await db.execute(stmt)
    contract = res.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found for this gig")

    if (
        current_user.id != contract.poster_id
        and current_user.id != contract.doer_id
        and current_user.role != "admin"
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return contract


@router.post("/{contract_id}/confirm", response_model=ContractRead, summary="Poster or Doer confirms agreement terms")
async def confirm_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Contract)
        .where(Contract.id == contract_id)
        .options(
            selectinload(Contract.poster),
            selectinload(Contract.doer),
            selectinload(Contract.deliverables),
            selectinload(Contract.payment),
            selectinload(Contract.gig),
        )
    )
    res = await db.execute(stmt)
    contract = res.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    is_poster = current_user.id == contract.poster_id
    is_doer = current_user.id == contract.doer_id

    if not is_poster and not is_doer and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only contract participants can confirm the agreement",
        )

    now = datetime.now(timezone.utc)
    if is_poster:
        contract.confirmed_by_poster_at = now
    if is_doer:
        contract.confirmed_by_doer_at = now

    # When both sides confirm, transition contract to active and gig to InProgress
    if contract.confirmed_by_poster_at and contract.confirmed_by_doer_at:
        contract.status = ContractStatus.ACTIVE

        # Fetch gig and transition
        gig_stmt = select(Gig).where(Gig.id == contract.gig_id)
        gig = (await db.execute(gig_stmt)).scalar_one()

        check_valid_transition(gig.status, GigStatus.InProgress)
        gig.status = GigStatus.InProgress

    await db.commit()
    await db.refresh(contract)
    return contract
