import logging
import re
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator
from typing import Optional

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # ── Core ──────────────────────────────────────────────────
    app_env: str = "development"
    frontend_origin: str = "http://localhost:3000"
    log_level: str = "INFO"

    # ── Database (required) ──────────────────────────────────
    database_url: str
    database_url_direct: Optional[str] = None

    # ── AI Provider ──────────────────────────────────────────
    ai_provider: str = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = ""
    gemini_fallback_model: str = ""
    nvidia_api_key: str = ""
    nvidia_model: str = "meta/llama-3.2-90b-vision-instruct"
    openrouter_api_key: str = ""
    openrouter_model: str = "moonshotai/kimi-k2.6:free"

    # ── Object Storage (S3 / R2) ─────────────────────────────
    storage_provider: str = "s3"
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket: str = ""
    r2_endpoint: str = ""
    signed_url_expiry_seconds: int = 3600

    # ── Email (Resend) ───────────────────────────────────────
    email_provider: str = "resend"
    resend_api_key: str = ""
    resend_from_email: str = ""
    resend_from_name: str = "SkinScan"

    # ── Google OAuth ─────────────────────────────────────────
    google_oauth_client_id: str = ""
    oauth_redirect_uri: str = ""

    # ── JWT (required) ───────────────────────────────────────
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 720

    # ── Turnstile CAPTCHA ────────────────────────────────────
    turnstile_secret_key: str = ""

    # ── Razorpay Payments ────────────────────────────────────
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""

    # ── Rate Limiting ────────────────────────────────────────
    rate_limit_per_email_per_day: int = 30
    premium_rate_limit_per_email_per_day: int = 7 # Fair Use Policy for Premium
    rate_limit_per_ip_per_day: int = 10

    # ── Data Retention ───────────────────────────────────────
    photo_retention_days: int = 365

    # ── Upload Limits ────────────────────────────────────────
    max_upload_bytes: int = 10 * 1024 * 1024  # 10 MB

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # ── Validators ───────────────────────────────────────────
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith("postgresql://") and not v.startswith("postgres://"):
            raise ValueError(
                "DATABASE_URL must start with postgresql:// or postgres://"
            )
        return v

    @field_validator("frontend_origin")
    @classmethod
    def validate_frontend_origin(cls, v: str) -> str:
        if v and not re.match(r"^https?://", v):
            raise ValueError("FRONTEND_ORIGIN must be a valid URL (http:// or https://)")
        return v

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 16:
            raise ValueError("JWT_SECRET must be at least 16 characters")
        return v

    @model_validator(mode="after")
    def validate_integrations(self):
        # Gemini: if provider is gemini, key must be present
        if self.ai_provider == "gemini" and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required when AI_PROVIDER=gemini")
        return self

    # ── Properties ───────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def storage_configured(self) -> bool:
        return bool(self.r2_access_key_id and self.r2_secret_access_key and self.r2_bucket)

    @property
    def email_configured(self) -> bool:
        return bool(self.resend_api_key and self.resend_from_email)

    @property
    def turnstile_configured(self) -> bool:
        return bool(self.turnstile_secret_key)


def run_startup_checks(s: Settings) -> None:
    """Log which integrations are configured (without leaking secret values)."""
    logger.info("=" * 50)
    logger.info("SkinScan API — Startup Integration Check")
    logger.info("=" * 50)
    logger.info(f"  Environment   : {s.app_env}")
    logger.info(f"  Frontend CORS : {s.frontend_origin}")
    logger.info(f"  Database      : {'✓ configured' if s.database_url else '✗ MISSING'}")
    logger.info(f"  AI Provider   : {s.ai_provider} — {'✓ key present' if s.openrouter_api_key else '✗ key missing'}")
    logger.info(f"  Model         : {s.openrouter_model}")
    logger.info(f"  Object Storage: {'✓ configured' if s.storage_configured else '○ not configured (photo save disabled)'}")
    logger.info(f"  Email (Resend): {'✓ configured' if s.email_configured else '○ not configured (emails disabled)'}")
    logger.info(f"  Turnstile     : {'✓ configured' if s.turnstile_configured else '○ not configured (CAPTCHA bypassed)'}")
    logger.info(f"  Google OAuth  : {'✓ client ID present' if s.google_oauth_client_id else '○ not configured'}")
    logger.info(f"  Rate Limits   : {s.rate_limit_per_email_per_day}/email/day, {s.rate_limit_per_ip_per_day}/ip/day")
    logger.info("=" * 50)
 


settings = Settings()
