import enum
from typing import Optional
from sqlalchemy import String, Integer, Float, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import CommonBase


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Application(CommonBase):
    __tablename__ = "applications"

    gig_id: Mapped[str] = mapped_column(String(36), ForeignKey("gigs.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    pitch: Mapped[str] = mapped_column(Text, nullable=False)
    sample_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    proposed_price: Mapped[int] = mapped_column(Integer, nullable=False)
    proposed_days: Mapped[int] = mapped_column(Integer, nullable=False)
    
    fit_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fit_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    status: Mapped[ApplicationStatus] = mapped_column(
        SQLEnum(ApplicationStatus),
        default=ApplicationStatus.PENDING,
        nullable=False,
    )

    # Relationships
    gig: Mapped["Gig"] = relationship("Gig", back_populates="applications")
    user: Mapped["User"] = relationship("User", back_populates="applications")
