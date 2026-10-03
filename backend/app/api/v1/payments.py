from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.contract import Contract, PaymentRecord
from app.schemas.contract import PaymentRecordRead

router = APIRouter(prefix="/contracts/{contract_id}/payment", tags=["Payment Record-Keeping"])


async def get_or_create_payment(contract_id: str, db: AsyncSession) -> PaymentRecord:
    c_stmt = select(Contract).where(Contract.id == contract_id)
    contract = (await db.execute(c_stmt)).scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    pay_stmt = select(PaymentRecord).where(PaymentRecord.contract_id == contract_id)
    payment = (await db.execute(pay_stmt)).scalar_one_or_none()
    if not payment:
        payment = PaymentRecord(
            contract_id=contract.id,
            amount=contract.agreed_price,
            method="upi_direct",
            status="pending",
        )
        db.add(payment)
        await db.commit()
        await db.refresh(payment)

    return payment


@router.get("", response_model=PaymentRecordRead, summary="View payment record status")
async def get_payment_record(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = await get_or_create_payment(contract_id, db)
    return payment


@router.post("/paid", response_model=PaymentRecordRead, summary="Poster records having sent UPI payment directly")
async def mark_paid_by_poster(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c_stmt = select(Contract).where(Contract.id == contract_id)
    contract = (await db.execute(c_stmt)).scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    if current_user.id != contract.poster_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the poster can mark payment as sent")

    payment = await get_or_create_payment(contract_id, db)
    payment.poster_marked_paid = True
    payment.poster_marked_paid_at = datetime.now(timezone.utc)

    if payment.doer_marked_received:
        payment.status = "completed"

    await db.commit()
    await db.refresh(payment)
    return payment


@router.post("/received", response_model=PaymentRecordRead, summary="Doer records having received UPI payment directly")
async def mark_received_by_doer(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c_stmt = select(Contract).where(Contract.id == contract_id)
    contract = (await db.execute(c_stmt)).scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    if current_user.id != contract.doer_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the doer can confirm receipt of payment")

    payment = await get_or_create_payment(contract_id, db)
    payment.doer_marked_received = True
    payment.doer_marked_received_at = datetime.now(timezone.utc)

    if payment.poster_marked_paid:
        payment.status = "completed"

    await db.commit()
    await db.refresh(payment)
    return payment
