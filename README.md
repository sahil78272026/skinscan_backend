# SkinScan API

Backend for SkinScan application.

## Local Run

1. Copy `.env.example` to `.env` and fill values.
2. `python3 -m venv venv && source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `alembic upgrade head`
5. `uvicorn app.main:app --reload` or uvicorn app.main:app --host 0.0.0.0 --reload

## Deploy

1. Ensure `.env` is set in production.
2. `docker-compose up -d --build`
