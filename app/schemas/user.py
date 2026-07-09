from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None
    consent_analysis: bool = False
class UserCreate(UserBase):
    google_id: Optional[str] = None

class UserOut(UserBase):
    id: UUID
    created_at: datetime
    last_active_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DeleteDataRequest(BaseModel):
    confirm: bool
