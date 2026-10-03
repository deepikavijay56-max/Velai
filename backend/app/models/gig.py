from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import CommonBase
from app.core.state_machine import GigStatus


class Gig(CommonBase):
    __tablename__ = "gigs"

    college_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    org_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    poster_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    deliverables: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)  # List of deliverable bullet points
    
    budget_min: Mapped[int] = mapped_column(Integer, nullable=False)
    budget_max: Mapped[int] = mapped_column(Integer, nullable=False)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revisions: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    status: Mapped[GigStatus] = mapped_column(
        SQLEnum(GigStatus),
        default=GigStatus.Open,
        nullable=False,
        index=True,
    )
    
    # Trust & Safety
    is_flagged_academic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    flag_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    ai_brief: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="gigs")
    poster: Mapped["User"] = relationship("User", foreign_keys=[poster_id])
    skills: Mapped[List["GigSkill"]] = relationship("GigSkill", back_populates="gig", cascade="all, delete-orphan")
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="gig", cascade="all, delete-orphan")
    contract: Mapped[Optional["Contract"]] = relationship("Contract", back_populates="gig", uselist=False)
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="gig", cascade="all, delete-orphan")


class GigSkill(CommonBase):
    __tablename__ = "gig_skills"

    gig_id: Mapped[str] = mapped_column(String(36), ForeignKey("gigs.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    gig: Mapped["Gig"] = relationship("Gig", back_populates="skills")
