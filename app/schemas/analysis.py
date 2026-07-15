from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID

class ZoneObservation(BaseModel):
    observations: List[str]
    severity: str

class ZoneBreakdown(BaseModel):
    forehead: Optional[ZoneObservation] = None
    t_zone: Optional[ZoneObservation] = None
    left_cheek: Optional[ZoneObservation] = None
    right_cheek: Optional[ZoneObservation] = None
    under_eye: Optional[ZoneObservation] = None
    chin_jawline: Optional[ZoneObservation] = None

class Routine(BaseModel):
    morning: List[str]
    evening: List[str]

class AnalysisResult(BaseModel):
    image_quality: str
    skin_type: Optional[str] = None
    skin_tone: Optional[str] = None
    zones: Optional[ZoneBreakdown] = None
    top_concerns: List[str] = Field(default_factory=list)
    focus_areas: List[str] = Field(default_factory=list)
    routine: Optional[Routine] = None
    lifestyle_nudges: List[str] = Field(default_factory=list)
    encouragement_note: Optional[str] = None
    recommended_products: List[dict] = Field(default_factory=list)

class AnalysisCreate(BaseModel):
    user_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    skin_type: Optional[str]
    skin_tone: Optional[str]
    result_json: dict
    top_concerns: List[str]
    age_range: Optional[str] = None
    primary_concern: Optional[str] = None
    region_country: Optional[str] = None
    region_state: Optional[str] = None
    photo_object_key: Optional[str] = None
    ai_provider: str
    consent_photo: Optional[bool] = None
    consent_photo_given_at: Optional[datetime] = None
    overall_score: Optional[int] = None

class AnalysisOut(BaseModel):
    id: UUID
    created_at: datetime
    skin_type: Optional[str]
    skin_tone: Optional[str]
    result_json: dict
    top_concerns: List[str]
    photo_object_key: Optional[str] = None
    photo_url: Optional[str] = None
    user_id: Optional[UUID] = None
    consent_photo: Optional[bool] = None
    consent_photo_given_at: Optional[datetime] = None
    overall_score: Optional[int] = None
    
    class Config:
        from_attributes = True
