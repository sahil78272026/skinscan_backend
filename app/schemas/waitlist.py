from pydantic import BaseModel, EmailStr, ConfigDict
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
    
    model_config = ConfigDict(from_attributes=True)
