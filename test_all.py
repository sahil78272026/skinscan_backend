import time
import requests
from sqlalchemy import text
from app.db.session import engine

print("1. Testing Database (Supabase)...")
start = time.time()
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print(f"✅ Database connected in {time.time() - start:.2f} seconds")
except Exception as e:
    print(f"❌ Database failed: {e}")

print("\n2. Testing Google Auth API...")
start = time.time()
try:
    resp = requests.get("https://www.googleapis.com/oauth2/v3/certs", timeout=5)
    print(f"✅ Google API connected in {time.time() - start:.2f} seconds (Status: {resp.status_code})")
except Exception as e:
    print(f"❌ Google API failed: {e}")

