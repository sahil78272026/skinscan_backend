import uuid
import logging
from io import BytesIO
from PIL import Image
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from app.schemas.analysis import AnalysisResult, AnalysisCreate, AnalysisOut
from app.models.user import User
from app.providers.base_ai import SkinAnalyzer
from app.providers.base_storage import StorageService
from app.providers.base_email import EmailService
from app.services.sanitizer import sanitize_analysis
from app.repositories.analysis_repository import AnalysisRepository
from app.core.exceptions import BadRequestException
from app.config import settings

logger = logging.getLogger(__name__)

def compress_image(file_bytes: bytes) -> bytes:
    try:
        img = Image.open(BytesIO(file_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        img.thumbnail((1024, 1024))
        
        out_io = BytesIO()
        img.save(out_io, format="JPEG", quality=85)
        return out_io.getvalue()
    except Exception as e:
        logger.error(f"Failed to compress image: {e}")
        raise BadRequestException("Invalid image file")

class AnalysisService:
    def __init__(
        self, 
        analyzer: SkinAnalyzer, 
        storage: StorageService, 
        email_svc: EmailService,
        db: Session
    ):
        self.analyzer = analyzer
        self.storage = storage
        self.email_svc = email_svc
        self.db = db
        self.repo = AnalysisRepository()

    async def orchestrate_analysis(
        self, 
        user: User | None, 
        file_bytes: bytes, 
        mime_type: str,
        background_tasks: BackgroundTasks,
        ip_address: str,
        age_range: str | None = None,
        primary_concern: str | None = None
    ) -> AnalysisOut:
        
        # 1. Compress image
        compressed_bytes = compress_image(file_bytes)
        
        photo_key = None
        # 2. If photo consent, upload
        if user and user.consent_photo_storage:
            photo_key = f"analyses/{user.id}/{uuid.uuid4()}.jpg"
            await self.storage.upload(compressed_bytes, photo_key, "image/jpeg")

        try:
            # 3. Analyze with AI
            ai_result = await self.analyzer.analyze(compressed_bytes, "image/jpeg")
            
            # 4. Check if valid face
            if ai_result.image_quality in ["poor", "not_a_face"]:
                raise BadRequestException(f"Image quality insufficient: {ai_result.image_quality}. Please retake.")
                
            # 5. Sanitize
            sanitized_result = sanitize_analysis(ai_result)
            
            # 6. Persist
            analysis_in = AnalysisCreate(
                user_id=user.id if user else None,
                ip_address=ip_address,
                skin_type=sanitized_result.skin_type,
                skin_tone=sanitized_result.skin_tone,
                result_json=sanitized_result.model_dump(),
                top_concerns=sanitized_result.top_concerns,
                age_range=age_range,
                primary_concern=primary_concern,
                photo_object_key=photo_key,
                ai_provider=settings.ai_provider
            )
            analysis_db = self.repo.create(self.db, analysis_in)
            
            # 7. Email Report
            if user:
                background_tasks.add_task(self.email_svc.send_report, user, sanitized_result)
            
            return AnalysisOut.model_validate(analysis_db)
            
        except Exception as e:
            # Cleanup storage on failure
            if photo_key:
                await self.storage.delete(photo_key)
            if isinstance(e, BadRequestException):
                raise e
            logger.error(f"Analysis orchestration failed: {e}")
            raise BadRequestException("Failed to process analysis")
