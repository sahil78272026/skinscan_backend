from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class AnalyticsEventCreate(BaseModel):
    session_id: str
    event_name: str
    page_url: Optional[str] = None
    metadata_payload: Optional[Dict[str, Any]] = None

class AnalyticsEventOut(BaseModel):
    id: UUID
    session_id: str
    user_id: Optional[UUID] = None
    event_name: str
    page_url: Optional[str] = None
    metadata_payload: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
