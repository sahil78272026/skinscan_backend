import asyncio
from app.config import settings
from app.services.turnstile import verify_turnstile

async def main():
    print("Secret Key:", settings.turnstile_secret_key)
    res = await verify_turnstile("XXXX.DUMMY.TOKEN.XXXX")
    print("Verification result:", res)

asyncio.run(main())
