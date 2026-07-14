import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.analytics import AnalyticsEvent

client = TestClient(app)

def test_track_analytics_event_anonymous():
    # 1. Arrange: Prepare the fake payload
    payload = {
        "session_id": "test_session_123",
        "event_name": "page_view_landing",
        "page_url": "/home"
    }

    # 2. Act: Send the fake request to the API
    response = client.post("/api/v1/analytics/track", json=payload)

    # 3. Assert: Check if the API responded correctly
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["data"]["status"] == "tracked"

    # 4. Verify Database (Optional but recommended): Make sure it actually saved!
    db = SessionLocal()
    saved_event = db.query(AnalyticsEvent).filter(AnalyticsEvent.session_id == "test_session_123").first()
    
    assert saved_event is not None
    assert saved_event.event_name == "page_view_landing"
    
    db.close()
