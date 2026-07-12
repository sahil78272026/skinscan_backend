from sqlalchemy.orm import Session
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisCreate
from typing import List
from uuid import UUID

class AnalysisRepository:
    def create(self, db: Session, obj_in: AnalysisCreate) -> Analysis:
        analysis = Analysis(
            user_id=obj_in.user_id,
            skin_type=obj_in.skin_type,
            skin_tone=obj_in.skin_tone,
            result_json=obj_in.result_json,
            top_concerns=obj_in.top_concerns,
            age_range=obj_in.age_range,
            primary_concern=obj_in.primary_concern,
            region_country=obj_in.region_country,
            region_state=obj_in.region_state,
            photo_object_key=obj_in.photo_object_key,
            ai_provider=obj_in.ai_provider,
            consent_photo=obj_in.consent_photo,
            consent_photo_given_at=obj_in.consent_photo_given_at,
            overall_score=obj_in.overall_score
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis

    def get_by_user(self, db: Session, user_id: UUID) -> List[Analysis]:
        return db.query(Analysis).filter(Analysis.user_id == user_id).all()

    def get_by_id(self, db: Session, analysis_id: UUID) -> Analysis:
        return db.query(Analysis).filter(Analysis.id == analysis_id).first()
