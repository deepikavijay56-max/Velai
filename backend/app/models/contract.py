import enum
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, Enum as SQLEnum, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import CommonBase


class ContractStatus(str, enum.Enum):
    PENDING_CONFIRMATION = "pending_confirmation"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DeliverableStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REVISION_REQUESTED = "revision_requested"


class Contract(CommonBase):
    __tablename__ = "contracts"

    college_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    gig_id: Mapped[str] = mapped_column(String(36), ForeignKey("gigs.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    poster_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    doer_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    agreed_price: Mapped[int] = mapped_column(Integer, nullable=False)
    agreed_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    agreed_revisions: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    revisions_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    confirmed_by_poster_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmed_by_doer_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    status: Mapped[ContractStatus] = mapped_column(
        SQLEnum(ContractStatus),
        default=ContractStatus.PENDING_CONFIRMATION,
        nullable=False,
    )

    # Relationships
    gig: Mapped["Gig"] = relationship("Gig", back_populates="contract")
    poster: Mapped["User"] = relationship("User", foreign_keys=[poster_id])
    doer: Mapped["User"] = relationship("User", foreign_keys=[doer_id])
    deliverables: Mapped[List["Deliverable"]] = relationship("Deliverable", back_populates="contract", cascade="all, delete-orphan")
    payment: Mapped[Optional["PaymentRecord"]] = relationship("PaymentRecord", back_populates="contract", uselist=False, cascade="all, delete-orphan")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="contract", cascade="all, delete-orphan")


class Deliverable(CommonBase):
    __tablename__ = "deliverables"

    contract_id: Mapped[str] = mapped_column(String(36), ForeignKey("contracts.id", ondelete="CASCADE"), index=True, nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    status: Mapped[DeliverableStatus] = mapped_column(
        SQLEnum(DeliverableStatus),
        default=DeliverableStatus.SUBMITTED,
        nullable=False,
    )
    revision_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    contract: Mapped["Contract"] = relationship("Contract", back_populates="deliverables")


class PaymentRecord(CommonBase):
    """
    Phase 1 Rule: Payments are RECORD-ONLY outside the app (e.g. direct UPI).
    Poster taps 'paid' and Doer taps 'received'.
    """
    __tablename__ = "payments"

    contract_id: Mapped[str] = mapped_column(String(36), ForeignKey("contracts.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    method: Mapped[str] = mapped_column(String(50), default="upi_direct", nullable=False)
    
    poster_marked_paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    poster_marked_paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    doer_marked_received: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    doer_marked_received_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, completed

    contract: Mapped["Contract"] = relationship("Contract", back_populates="payment")
