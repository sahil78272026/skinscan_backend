import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.analysis import Analysis
from app.models.user import User
from app.core.exceptions import RateLimitException

logger = logging.getLogger(__name__)


def check_rate_limit_email(db: Session, user: User, limit: int) -> None:
    """Raises RateLimitException if the user has exceeded their daily analysis limit."""
    if limit <= 0:
        return

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    count = (
        db.query(func.count(Analysis.id))
        .filter(Analysis.user_id == user.id, Analysis.created_at >= today_start)
        .scalar()
    )
    if count >= limit:
        raise RateLimitException(
            f"You've reached your daily limit of {limit} scan(s). Please try again tomorrow."
        )


def check_rate_limit_ip(db: Session, ip: str, limit: int) -> None:
    if limit <= 0:
        return
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    count = (
        db.query(func.count(Analysis.id))
        .filter(Analysis.ip_address == ip, Analysis.created_at >= today_start)
        .scalar()
    )
    if count >= limit:
        raise RateLimitException(
            f"You've reached the free daily limit of {limit} scan(s) for this IP. Please try again tomorrow."
        )
