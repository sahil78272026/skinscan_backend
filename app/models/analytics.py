from sqlalchemy import Column, String, DateTime, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from app.db.base import Base

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_name = Column(String(255), nullable=False, index=True)
    page_url = Column(String(1024), nullable=True)
    metadata_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Indexes to make funnel querying extremely fast
    __table_args__ = (
        Index("ix_analytics_session_event", "session_id", "event_name"),
    )
