from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.gig import Gig, GigStatus
from app.models.contract import Contract, ContractStatus, Deliverable, DeliverableStatus, PaymentRecord
from app.core.state_machine import check_valid_transition, validate_revision_limit
from app.schemas.contract import DeliverableCreate, DeliverableReviseRequest, DeliverableRead

router = APIRouter(tags=["Deliverables & Revisions"])


@router.post("/contracts/{contract_id}/deliver", response_model=DeliverableRead, summary="Doer submits gig deliverable")
async def submit_deliverable(
    contract_id: str,
    payload: DeliverableCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Fetch contract with gig
    c_stmt = select(Contract).where(Contract.id == contract_id).options(selectinload(Contract.gig))
    c_res = await db.execute(c_stmt)
    contract = c_res.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    if current_user.id != contract.doer_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the assigned doer can deliver work")

    if contract.status != ContractStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot deliver work: contract is in '{contract.status.value}' status",
        )

    # Transition gig state InProgress -> Delivered
    gig = contract.gig
    check_valid_transition(gig.status, GigStatus.Delivered)
    gig.status = GigStatus.Delivered

    # Calculate version number
    v_stmt = select(func.count(Deliverable.id)).where(Deliverable.contract_id == contract.id)
    v_res = await db.execute(v_stmt)
    current_version_count = v_res.scalar_one() or 0
    version = current_version_count + 1

    deliverable = Deliverable(
        contract_id=contract.id,
        file_url=payload.file_url.strip(),
        note=payload.note,
        version=version,
        status=DeliverableStatus.SUBMITTED,
    )
    db.add(deliverable)
    await db.commit()
    await db.refresh(deliverable)

    return deliverable


@router.post("/deliverables/{deliverable_id}/approve", response_model=DeliverableRead, summary="Poster approves deliverable")
async def approve_deliverable(
    deliverable_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Deliverable)
        .where(Deliverable.id == deliverable_id)
        .options(selectinload(Deliverable.contract).selectinload(Contract.gig))
    )
    res = await db.execute(stmt)
    deliverable = res.scalar_one_or_none()
    if not deliverable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deliverable not found")

    contract = deliverable.contract
    if current_user.id != contract.poster_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the gig poster can approve deliverables")

    if deliverable.status != DeliverableStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Deliverable already has status '{deliverable.status.value}'",
        )

    deliverable.status = DeliverableStatus.ACCEPTED

    # Transition gig state Delivered -> Completed
    gig = contract.gig
    check_valid_transition(gig.status, GigStatus.Completed)
    gig.status = GigStatus.Completed
    contract.status = ContractStatus.COMPLETED

    # Ensure PaymentRecord exists for record-keeping
    pay_stmt = select(PaymentRecord).where(PaymentRecord.contract_id == contract.id)
    pay_rec = (await db.execute(pay_stmt)).scalar_one_or_none()
    if not pay_rec:
        payment = PaymentRecord(
            contract_id=contract.id,
            amount=contract.agreed_price,
            method="upi_direct",
            status="pending",
        )
        db.add(payment)

    # Increment student completed gigs count
    doer_stmt = select(User).where(User.id == contract.doer_id)
    doer = (await db.execute(doer_stmt)).scalar_one_or_none()
    if doer:
        doer.completed_gigs_count += 1

    await db.commit()
    await db.refresh(deliverable)
    return deliverable


@router.post("/deliverables/{deliverable_id}/revise", response_model=DeliverableRead, summary="Poster requests revision")
async def request_revision(
    deliverable_id: str,
    payload: DeliverableReviseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Deliverable)
        .where(Deliverable.id == deliverable_id)
        .options(selectinload(Deliverable.contract).selectinload(Contract.gig))
    )
    res = await db.execute(stmt)
    deliverable = res.scalar_one_or_none()
    if not deliverable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deliverable not found")

    contract = deliverable.contract
    if current_user.id != contract.poster_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the poster can request revisions")

    # Enforce strictly the agreed revision limit
    validate_revision_limit(
        agreed_revisions=contract.agreed_revisions,
        revisions_used=contract.revisions_used,
    )

    # Transition gig state Delivered -> InProgress
    gig = contract.gig
    check_valid_transition(gig.status, GigStatus.InProgress)
    gig.status = GigStatus.InProgress

    deliverable.status = DeliverableStatus.REVISION_REQUESTED
    deliverable.revision_reason = payload.revision_reason.strip()

    # Increment revisions used
    contract.revisions_used += 1

    await db.commit()
    await db.refresh(deliverable)
    return deliverable
