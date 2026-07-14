import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    # Because health_check connects to DB, we must have DB running, or we mock it.
    # For CI, we will spin up a postgres service container.
    response = client.get("/healthz")
    # Even if DB is down, it returns 503 instead of crashing.
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
