import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, func, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from app.db.base import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    skin_type = Column(String, nullable=True)
    skin_tone = Column(String, nullable=True)
    result_json = Column(JSONB, nullable=False)
    top_concerns = Column(ARRAY(Text), nullable=True)
    
    age_range = Column(String, nullable=True)
    primary_concern = Column(String, nullable=True)
    region_country = Column(String, nullable=True)
    region_state = Column(String, nullable=True)
    
    photo_object_key = Column(String, nullable=True)
    ai_provider = Column(String, nullable=False)
    
    consent_photo = Column(Boolean, nullable=True)
    consent_photo_given_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", backref="analyses")
