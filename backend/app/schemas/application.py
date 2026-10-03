from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.application import ApplicationStatus
from app.schemas.contract import ContractUserSummary


class ApplicationCreate(BaseModel):
    pitch: str = Field(..., min_length=10)
    sample_url: Optional[str] = None
    proposed_price: int = Field(..., gt=0)
    proposed_days: int = Field(..., gt=0)


class ApplicationRead(BaseModel):
    id: str
    gig_id: str
    user_id: str
    pitch: str
    sample_url: Optional[str] = None
    proposed_price: int
    proposed_days: int
    fit_score: Optional[float] = None
    fit_reason: Optional[str] = None
    status: ApplicationStatus
    created_at: datetime
    user: Optional[ContractUserSummary] = None

    model_config = {"from_attributes": True}
