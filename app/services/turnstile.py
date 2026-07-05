import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)

async def verify_turnstile(token: str) -> bool:
    if not settings.turnstile_secret_key:
        return True # Skip if not configured
        
    if settings.turnstile_secret_key == "dummy" or token == "XXXX.DUMMY.TOKEN.XXXX":
        return True # Skip for testing
        
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={
                    "secret": settings.turnstile_secret_key,
                    "response": token
                }
            )
            result = response.json()
            return result.get("success", False)
    except Exception as e:
        logger.error(f"Turnstile verification failed: {e}")
        return False
