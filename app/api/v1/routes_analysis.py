from fastapi import APIRouter, Depends, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db, get_analyzer, get_storage, get_email
from app.models.user import User
from app.schemas.analysis import AnalysisOut
from app.schemas.response import Envelope, success_response
from app.services.analysis_service import AnalysisService
from app.services.turnstile import verify_turnstile
from app.services.rate_limiter import check_rate_limit_email
from app.providers.base_ai import SkinAnalyzer
from app.providers.base_storage import StorageService
from app.providers.base_email import EmailService
from app.core.exceptions import BadRequestException
from app.config import settings

router = APIRouter()

@router.post("/", response_model=Envelope[AnalysisOut])
async def create_analysis(
    request: Request,
    file: UploadFile = File(...),
    turnstile_token: str = Form(None),
    age_range: str = Form(None),
    primary_concern: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    analyzer: SkinAnalyzer = Depends(get_analyzer),
    storage: StorageService = Depends(get_storage),
    email_svc: EmailService = Depends(get_email)
):
    # 1. CAPTCHA verification
    if not await verify_turnstile(turnstile_token):
        raise BadRequestException("Invalid CAPTCHA")

    # 2. Rate limit check
    check_rate_limit_email(db, current_user, settings.rate_limit_per_email_per_day)

    # 3. Read and validate file size
    file_bytes = await file.read()
    if not file_bytes:
        raise BadRequestException("Empty file")
    if len(file_bytes) > settings.max_upload_bytes:
        max_mb = settings.max_upload_bytes // (1024 * 1024)
        raise BadRequestException(f"File too large. Maximum size is {max_mb}MB.")

    # 4. Validate content type
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}
    if file.content_type and file.content_type not in allowed_types:
        raise BadRequestException("Unsupported image format. Please upload a JPEG, PNG, or WebP image.")

    # 5. Run analysis
    service = AnalysisService(analyzer, storage, email_svc, db)
    analysis_out = await service.orchestrate_analysis(
        current_user, file_bytes, file.content_type or "image/jpeg", age_range, primary_concern
    )

    return success_response(analysis_out)
