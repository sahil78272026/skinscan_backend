import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.core.dependencies import get_optional_user, get_db, get_analyzer, get_storage
from app.models.user import User
import uuid
from io import BytesIO

client = TestClient(app)

@pytest.fixture
def mock_user():
    return User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        subscription_tier="premium",
        scans_used=5
    )

def test_create_analysis_success(mock_user):
    """Test the full analysis route via API with mocked dependencies."""
    
    # Create Mocks
    mock_db = MagicMock()
    mock_analyzer = MagicMock()
    mock_storage = MagicMock()
    
    # Setup Analyzer Mock
    mock_analyzer.analyze_image.return_value = {
        "image_quality": "good",
        "top_concerns": ["dryness"],
        "lifestyle_nudges": [],
        "recommended_products": []
    }
    
    # Setup Storage Mock
    mock_storage.upload_file.return_value = "mock_r2_key.jpg"
    
    # Apply Overrides
    app.dependency_overrides[get_optional_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_analyzer] = lambda: mock_analyzer
    app.dependency_overrides[get_storage] = lambda: mock_storage
    
    try:
        # We also need to mock turnstile to bypass security check
        with patch("app.api.v1.routes_analysis.settings") as mock_settings:
            mock_settings.turnstile_configured = False
            mock_settings.premium_rate_limit_per_email_per_day = 100
            mock_settings.rate_limit_per_ip_per_day = 10
            mock_settings.max_upload_bytes = 10485760
            
            with patch("app.api.v1.routes_analysis.check_rate_limit_email"):
                
                # We need a fake image file
                fake_image = BytesIO(b"fake image data")
                
                response = client.post(
                    "/api/v1/analyze/",
                    files={"file": ("test.jpg", fake_image, "image/jpeg")}
                )
                
                assert response.status_code == 200
                data = response.json()
                
                assert data["success"] is True
                assert data["data"]["result_json"]["image_quality"] == "good"
                assert "recommended_products" in data["data"]["result_json"]
                
                # Verify Gemini was called
                mock_analyzer.analyze_image.assert_called_once()
                
    finally:
        # Clean up overrides
        app.dependency_overrides.clear()
