from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class WaitlistCreate(BaseModel):
    email: EmailStr
    interest: Optional[str] = None
    analysis_id: Optional[UUID] = None

class WaitlistOut(WaitlistCreate):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
