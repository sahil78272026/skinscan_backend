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
from app.services.product_recommender import get_recommendations_for_concerns
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

def calculate_skin_score(sanitized_result: AnalysisResult) -> int:
    score = 100
    if not sanitized_result.zones:
        return score
    
    for zone, observation in sanitized_result.zones.model_dump().items():
        if not observation:
            continue
        severity = observation.get("severity", "").lower()
        if severity == "severe":
            score -= 15
        elif severity == "moderate":
            score -= 8
        elif severity == "mild":
            score -= 3
            
    return max(0, score)

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
        primary_concern: str | None = None,
        consent_photo: bool = False
    ) -> AnalysisOut:
        
        # 1. Compress image
        compressed_bytes = compress_image(file_bytes)
        
        # 2. Upload photo (always upload so it can be claimed later)
        prefix = f"analyses/{user.id}" if user else "analyses/anonymous"
        photo_key = f"{prefix}/{uuid.uuid4()}.jpg"
        await self.storage.upload(compressed_bytes, photo_key, "image/jpeg")
        
        # If logged-in user explicitly opted out previously, OR current consent_photo is False, we'll delete it later or don't set it
        # Actually, let's respect the current consent_photo flag first, fallback to user.consent_photo_storage if user exists and consent_photo is somehow not provided (though it defaults to False).
        final_consent_photo = consent_photo
        if user and not final_consent_photo:
            # Let's say if it's False from UI but True in DB, we trust UI for this specific pic
            pass

        if not final_consent_photo:
            await self.storage.delete(photo_key)
            photo_key = None

        try:
            # 3. Analyze with AI
            ai_result = await self.analyzer.analyze(compressed_bytes, "image/jpeg")
            
            # 4. Check if valid face
            if ai_result.image_quality in ["poor", "not_a_face"]:
                raise BadRequestException(f"Image quality insufficient: {ai_result.image_quality}. Please retake.")
                
            # 5. Sanitize
            sanitized_result = sanitize_analysis(ai_result)
            
            # 5.5 Inject Recommended Products
            recommended = get_recommendations_for_concerns(sanitized_result.top_concerns)
            sanitized_result.recommended_products = recommended
            
            overall_score = calculate_skin_score(sanitized_result)
            
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
                ai_provider=settings.ai_provider,
                consent_photo=final_consent_photo,
                consent_photo_given_at=datetime.now(timezone.utc) if final_consent_photo else None,
                overall_score=overall_score
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
