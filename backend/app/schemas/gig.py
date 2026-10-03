from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from app.core.state_machine import GigStatus


class GigCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    category: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=15)
    deliverables: List[str] = Field(..., min_length=1, description="List of expected deliverables")
    budget_min: int = Field(..., gt=0)
    budget_max: int = Field(..., gt=0)
    deadline: datetime
    revisions: int = Field(1, ge=0, le=10)
    org_id: Optional[str] = None
    skills: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_budget_range(self) -> "GigCreate":
        if self.budget_min > self.budget_max:
            raise ValueError("budget_min cannot be greater than budget_max")
        return self


class GigUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    deliverables: Optional[List[str]] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    deadline: Optional[datetime] = None
    revisions: Optional[int] = None
    skills: Optional[List[str]] = None


class PosterSummary(BaseModel):
    id: str
    name: str
    college_email: str
    department: Optional[str] = None
    reputation: float

    model_config = {"from_attributes": True}


class OrgSummary(BaseModel):
    id: str
    name: str
    type: str
    verified_status: str

    model_config = {"from_attributes": True}


class GigRead(BaseModel):
    id: str
    college_id: str
    org_id: Optional[str] = None
    poster_id: str
    title: str
    category: str
    description: str
    deliverables: List[str]
    budget_min: int
    budget_max: int
    deadline: datetime
    revisions: int
    status: GigStatus
    is_flagged_academic: bool
    flag_reason: Optional[str] = None
    skills: List[str] = []
    poster: Optional[PosterSummary] = None
    organization: Optional[OrgSummary] = None
    applications_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
