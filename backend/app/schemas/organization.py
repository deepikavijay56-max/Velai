from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.organization import OrgType, OrgVerificationStatus


class OrgCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    type: OrgType
    description: Optional[str] = None
    logo_url: Optional[str] = None


class OrgApproveRequest(BaseModel):
    verified_status: OrgVerificationStatus = Field(..., description="approved or rejected")


class OrgRead(BaseModel):
    id: str
    college_id: str
    name: str
    type: OrgType
    description: Optional[str] = None
    verified_status: OrgVerificationStatus
    owner_id: str
    logo_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
