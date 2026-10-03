from typing import Optional, List
from sqlalchemy import String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import CommonBase


class Review(CommonBase):
    __tablename__ = "reviews"

    contract_id: Mapped[str] = mapped_column(String(36), ForeignKey("contracts.id", ondelete="CASCADE"), index=True, nullable=False)
    reviewer_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    reviewee_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 5
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)  # e.g. ["fast", "creative", "great communication"]

    contract: Mapped["Contract"] = relationship("Contract", back_populates="reviews")
    reviewer: Mapped["User"] = relationship("User", foreign_keys=[reviewer_id])
    reviewee: Mapped["User"] = relationship("User", foreign_keys=[reviewee_id])
