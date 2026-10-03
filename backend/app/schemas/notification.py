from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class NotificationRead(BaseModel):
    id: str
    user_id: str
    topic: str
    title: str
    body: str
    data: Dict[str, Any] = {}
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationPrefRead(BaseModel):
    user_id: str
    muted_topics: List[str]
    quiet_hours_start: Optional[int] = None
    quiet_hours_end: Optional[int] = None
    daily_count: int

    model_config = {"from_attributes": True}


class NotificationPrefUpdate(BaseModel):
    muted_topics: Optional[List[str]] = None
    quiet_hours_start: Optional[int] = Field(None, ge=0, le=23)
    quiet_hours_end: Optional[int] = Field(None, ge=0, le=23)


class DeviceRegister(BaseModel):
    fcm_token: str
    device_type: str = "mobile"
