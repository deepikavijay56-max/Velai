from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.contract import ContractStatus, DeliverableStatus


class ContractUserSummary(BaseModel):
    id: str
    name: str
    college_email: str
    department: Optional[str] = None
    role: str
    reputation: float

    model_config = {"from_attributes": True}


class DeliverableCreate(BaseModel):
    file_url: str = Field(..., description="Uploaded file URL or link")
    note: Optional[str] = None


class DeliverableReviseRequest(BaseModel):
    revision_reason: str = Field(..., min_length=5, description="Clear description of requested changes")


class DeliverableRead(BaseModel):
    id: str
    contract_id: str
    file_url: str
    note: Optional[str] = None
    version: int
    status: DeliverableStatus
    revision_reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentRecordRead(BaseModel):
    id: str
    contract_id: str
    amount: int
    method: str
    poster_marked_paid: bool
    poster_marked_paid_at: Optional[datetime] = None
    doer_marked_received: bool
    doer_marked_received_at: Optional[datetime] = None
    status: str

    model_config = {"from_attributes": True}


class ContractRead(BaseModel):
    id: str
    college_id: str
    gig_id: str
    poster_id: str
    doer_id: str
    agreed_price: int
    agreed_deadline: datetime
    agreed_revisions: int
    revisions_used: int
    confirmed_by_poster_at: Optional[datetime] = None
    confirmed_by_doer_at: Optional[datetime] = None
    status: ContractStatus
    created_at: datetime
    poster: Optional[ContractUserSummary] = None
    doer: Optional[ContractUserSummary] = None
    deliverables: List[DeliverableRead] = []
    payment: Optional[PaymentRecordRead] = None

    model_config = {"from_attributes": True}
