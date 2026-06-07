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

class AnalysisCreate(BaseModel):
    user_id: UUID
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

class AnalysisOut(BaseModel):
    id: UUID
    created_at: datetime
    skin_type: Optional[str]
    skin_tone: Optional[str]
    result_json: dict
    top_concerns: List[str]
    photo_object_key: Optional[str]
    
    class Config:
        from_attributes = True
