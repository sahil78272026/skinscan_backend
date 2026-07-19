import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.models.user import User
from app.config import settings
import uuid
import datetime

client = TestClient(app)

@pytest.fixture
def mock_user():
    return User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        subscription_tier="free",
        scans_used=0,
        created_at=datetime.datetime.now()
    )

def test_login_email_success(mock_user):
    """Test the email login route generates a valid token."""
    with patch("app.api.v1.routes_auth.AuthService") as MockAuthService:
        mock_auth_svc = MockAuthService.return_value
        mock_auth_svc.process_email_login.return_value = (mock_user, "mocked_jwt_token")
        
        response = client.post(
            "/api/v1/auth/email",
            data={
                "email": "test@example.com",
                "turnstile_token": "dummy_token"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["access_token"] == "mocked_jwt_token"
        assert data["data"]["token_type"] == "bearer"
        
        mock_auth_svc.process_email_login.assert_called_once_with("test@example.com", False)

def test_login_google_success(mock_user):
    """Test the Google OAuth login route."""
    with patch.object(settings, "google_oauth_client_id", "mock_client_id"):
        
        with patch("app.api.v1.routes_auth.AuthService") as MockAuthService:
            mock_auth_svc = MockAuthService.return_value
            mock_auth_svc.process_google_login.return_value = (mock_user, "mocked_google_jwt")
            
            response = client.post(
                "/api/v1/auth/google",
                data={
                    "credential": "mocked_google_credential"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["access_token"] == "mocked_google_jwt"
            
            mock_auth_svc.process_google_login.assert_called_once_with("mocked_google_credential", "mock_client_id", False)

def test_login_google_unconfigured():
    """Test Google login when the client ID is missing from .env."""
    with patch.object(settings, "google_oauth_client_id", ""):
        
        response = client.post(
            "/api/v1/auth/google",
            data={
                "credential": "mocked_google_credential"
            }
        )
        
        assert response.status_code == 400
        assert "Google login is not configured" in response.json()["error"]["message"]
