import pytest
from unittest.mock import patch, MagicMock
from fastapi import Request
from app.api.v1.routes_analysis import create_analysis
from app.core.exceptions import BadRequestException, RateLimitException
from app.models.user import User

@pytest.mark.asyncio
async def test_anonymous_user_rate_limit():
    """Test that anonymous users are blocked after 1 scan (Paywall trigger)."""
    mock_db = MagicMock()
    mock_request = MagicMock(spec=Request)
    mock_request.headers.get.return_value = "127.0.0.1"
    mock_request.client.host = "127.0.0.1"
    
    # Mock Turnstile to pass
    with patch("app.api.v1.routes_analysis.settings") as mock_settings:
        mock_settings.turnstile_configured = False
        
        # Mock check_rate_limit_ip to pass (not hit the daily 10 limit)
        with patch("app.services.rate_limiter.check_rate_limit_ip"):
            
            # Mock DB to return 1 anonymous scan for this IP
            mock_query = mock_db.query.return_value
            mock_filter = mock_query.filter.return_value
            mock_filter.count.return_value = 1
            
            with pytest.raises(BadRequestException) as exc_info:
                await create_analysis(
                    request=mock_request,
                    file=MagicMock(),
                    turnstile_token="dummy",
                    db=mock_db,
                    current_user=None, # Anonymous
                    storage=MagicMock(),
                    email_svc=MagicMock(),
                    background_tasks=MagicMock()
                )
            
            assert "Free scan used! Please sign up" in str(exc_info.value)

@pytest.mark.asyncio
async def test_free_user_rate_limit():
    """Test that free users are blocked after 3 lifetime scans."""
    mock_db = MagicMock()
    mock_request = MagicMock(spec=Request)
    
    mock_user = User(id="user1", email="test@test.com", subscription_tier="free", scans_used=3)
    
    with patch("app.api.v1.routes_analysis.settings") as mock_settings:
        mock_settings.turnstile_configured = False
        
        with patch("app.api.v1.routes_analysis.check_rate_limit_email"):
            
            with pytest.raises(BadRequestException) as exc_info:
                await create_analysis(
                    request=mock_request,
                    file=MagicMock(),
                    turnstile_token="dummy",
                    db=mock_db,
                    current_user=mock_user,
                    storage=MagicMock(),
                    email_svc=MagicMock(),
                    background_tasks=MagicMock()
                )
            
            assert "Out of free scans! Please upgrade to Premium" in str(exc_info.value)

@pytest.mark.asyncio
async def test_premium_user_fup_limit():
    """Test that premium users bypass the 3-scan limit but hit the 7/day FUP limit."""
    mock_db = MagicMock()
    mock_request = MagicMock(spec=Request)
    
    # User has 10 lifetime scans (bypasses the 3-scan free limit)
    mock_user = User(id="user2", email="premium@test.com", subscription_tier="premium", scans_used=10)
    
    with patch("app.api.v1.routes_analysis.settings") as mock_settings:
        mock_settings.turnstile_configured = False
        mock_settings.premium_rate_limit_per_email_per_day = 7
        
        # Mock check_rate_limit_email to raise RateLimitException (as if they did 7 today)
        with patch("app.api.v1.routes_analysis.check_rate_limit_email") as mock_rate_limit:
            mock_rate_limit.side_effect = RateLimitException("Mocked rate limit")
            
            with pytest.raises(BadRequestException) as exc_info:
                await create_analysis(
                    request=mock_request,
                    file=MagicMock(),
                    turnstile_token="dummy",
                    db=mock_db,
                    current_user=mock_user,
                    storage=MagicMock(),
                    email_svc=MagicMock(),
                    background_tasks=MagicMock()
                )
            
            assert "Fair Use Policy limit of 7 scans" in str(exc_info.value)
