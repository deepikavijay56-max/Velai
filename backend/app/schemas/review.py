from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=1000)
    tags: List[str] = Field(default_factory=list, description="Tags like 'fast', 'creative'")


class ReviewRead(BaseModel):
    id: str
    contract_id: str
    reviewer_id: str
    reviewee_id: str
    rating: int
    comment: Optional[str] = None
    tags: List[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}
