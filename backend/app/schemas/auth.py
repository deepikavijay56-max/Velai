from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class OTPRequest(BaseModel):
    email: EmailStr = Field(..., description="College email ending in configured domain")


class OTPVerify(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=4, max_length=10)
    name: Optional[str] = Field(None, description="Full name if first-time user")
    department: Optional[str] = None
    year: Optional[int] = None
    role: Optional[str] = Field("student", description="student, staff, or admin")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserRead"


class UserSkillCreate(BaseModel):
    skill_name: str
    level: str = Field("intermediate", description="beginner, intermediate, expert")
    sample_links: List[str] = Field(default_factory=list, max_length=3)


class UserSkillRead(BaseModel):
    id: str
    skill_name: str
    level: str
    sample_links: List[str]

    model_config = {"from_attributes": True}


class UserRead(BaseModel):
    id: str
    college_id: str
    college_email: str
    name: str
    department: Optional[str] = None
    year: Optional[int] = None
    role: str
    reputation: float
    completed_gigs_count: int
    availability: Optional[Dict[str, Any]] = None
    skills: List[UserSkillRead] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    year: Optional[int] = None
    availability: Optional[Dict[str, Any]] = None


TokenResponse.model_rebuild()
