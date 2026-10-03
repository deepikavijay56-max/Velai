from typing import Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import CommonBase


class Message(CommonBase):
    __tablename__ = "messages"

    gig_id: Mapped[str] = mapped_column(String(36), ForeignKey("gigs.id", ondelete="CASCADE"), index=True, nullable=False)
    sender_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    attachment_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    gig: Mapped["Gig"] = relationship("Gig", back_populates="messages")
    sender: Mapped["User"] = relationship("User")
