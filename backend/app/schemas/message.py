from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    body: str = Field(..., min_length=1)
    attachment_url: Optional[str] = None


class MessageRead(BaseModel):
    id: str
    gig_id: str
    sender_id: str
    sender_name: Optional[str] = None
    body: str
    attachment_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
