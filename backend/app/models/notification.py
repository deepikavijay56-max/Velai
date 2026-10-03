from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import CommonBase


class Notification(CommonBase):
    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    topic: Mapped[str] = mapped_column(String(50), nullable=False)  # new_gig, application, contract, chat, delivery
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User")


class NotificationPref(CommonBase):
    __tablename__ = "notification_prefs"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    muted_topics: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    quiet_hours_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # e.g. 23 (11 PM)
    quiet_hours_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)    # e.g. 7 (7 AM)
    daily_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_count_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # YYYY-MM-DD to reset daily


class Device(CommonBase):
    __tablename__ = "devices"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    fcm_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    device_type: Mapped[str] = mapped_column(String(50), default="mobile", nullable=False)
