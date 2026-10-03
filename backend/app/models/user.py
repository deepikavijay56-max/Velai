import enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import CommonBase


class UserRole(str, enum.Enum):
    STUDENT = "student"
    STAFF = "staff"
    ADMIN = "admin"


class User(CommonBase):
    __tablename__ = "users"

    college_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    college_email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1, 2, 3, 4, etc.
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.STUDENT,
        nullable=False,
    )
    reputation: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    completed_gigs_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    availability: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    skills: Mapped[List["UserSkill"]] = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    owned_orgs: Mapped[List["Organization"]] = relationship("Organization", back_populates="owner")
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="user")


class Skill(CommonBase):
    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)


class UserSkill(CommonBase):
    __tablename__ = "user_skills"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[str] = mapped_column(String(50), default="intermediate", nullable=False)  # beginner, intermediate, expert
    sample_links: Mapped[List[str]] = mapped_column(JSON, default=list)  # max 3 portfolio links

    user: Mapped["User"] = relationship("User", back_populates="skills")


class OTPVerification(CommonBase):
    __tablename__ = "otp_verifications"

    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    otp_code: Mapped[str] = mapped_column(String(10), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
