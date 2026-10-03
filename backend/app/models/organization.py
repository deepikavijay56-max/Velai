import enum
from typing import Optional, List
from sqlalchemy import String, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import CommonBase


class OrgType(str, enum.Enum):
    CLUB = "club"
    DEPARTMENT = "department"
    BUSINESS = "business"


class OrgVerificationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Organization(CommonBase):
    __tablename__ = "organizations"

    college_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    type: Mapped[OrgType] = mapped_column(SQLEnum(OrgType), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified_status: Mapped[OrgVerificationStatus] = mapped_column(
        SQLEnum(OrgVerificationStatus),
        default=OrgVerificationStatus.APPROVED,  # Clubs/Depts auto-approved or approved by default; businesses start pending
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="owned_orgs")
    members: Mapped[List["OrgMember"]] = relationship("OrgMember", back_populates="organization", cascade="all, delete-orphan")
    gigs: Mapped[List["Gig"]] = relationship("Gig", back_populates="organization")


class OrgMember(CommonBase):
    __tablename__ = "org_members"

    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="member", nullable=False)  # owner, admin, member

    organization: Mapped["Organization"] = relationship("Organization", back_populates="members")
