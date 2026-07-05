from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_optional_user, get_db, get_analyzer, get_storage, get_email
from app.models.user import User
from app.schemas.analysis import AnalysisOut
from app.schemas.response import Envelope, success_response
import uuid
from app.services.analysis_service import AnalysisService
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
    background_tasks: BackgroundTasks,
    turnstile_token: str | None = Form(None),
    file: UploadFile = File(...),
    age_range: str | None = Form(None),
    primary_concern: str | None = Form(None),
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
    analyzer: SkinAnalyzer = Depends(get_analyzer),
    storage: StorageService = Depends(get_storage),
    email_svc: EmailService = Depends(get_email)
):
    # Turnstile Check
    if settings.turnstile_configured:
        from app.services.turnstile import verify_turnstile
        is_human = await verify_turnstile(turnstile_token or "")
        if not is_human:
            raise BadRequestException("Security check failed (Turnstile)")

    # 2. Rate limit check
    client_ip = request.headers.get("x-real-ip") or request.client.host or "127.0.0.1"
    if current_user:
        check_rate_limit_email(db, current_user, settings.rate_limit_per_email_per_day)
    else:
        from app.services.rate_limiter import check_rate_limit_ip
        check_rate_limit_ip(db, client_ip, settings.rate_limit_per_ip_per_day)

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
        current_user, file_bytes, file.content_type or "image/jpeg", background_tasks, client_ip, age_range, primary_concern
    )

    return success_response(analysis_out)

@router.post("/claim", response_model=Envelope[dict])
async def claim_analysis(
    background_tasks: BackgroundTasks,
    job_id: uuid.UUID = Form(...),
    email: str = Form(...),
    consent_analysis: bool = Form(False),
    consent_photo: bool = Form(False),
    db: Session = Depends(get_db),
    email_svc: EmailService = Depends(get_email),
    storage: StorageService = Depends(get_storage)
):
    from app.services.auth_service import AuthService
    from app.repositories.analysis_repository import AnalysisRepository
    from app.schemas.analysis import AnalysisResult

    # 1. Login or create user
    auth_svc = AuthService(db)
    user, token = auth_svc.process_email_login(email, consent_analysis, consent_photo)
    
    # 2. Claim analysis
    repo = AnalysisRepository()
    job = repo.get_by_id(db, job_id)
    if not job:
        raise BadRequestException("Analysis not found")
        
    if job.user_id and job.user_id != user.id:
        raise BadRequestException("Analysis already claimed")
        
    if not job.user_id:
        job.user_id = user.id
        # Handle photo retention
        if not consent_photo and job.photo_object_key:
            background_tasks.add_task(storage.delete, job.photo_object_key)
            job.photo_object_key = None
        db.commit()
    
    # 3. Email report
    if job.result_json:
        sanitized_result = AnalysisResult(**job.result_json)
        background_tasks.add_task(email_svc.send_report, user, sanitized_result)
        
    return success_response({"access_token": token, "message": "Report claimed and emailed successfully"})
