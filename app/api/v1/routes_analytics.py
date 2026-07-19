from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_optional_user
from app.models.user import User
from app.models.analytics import AnalyticsEvent
from app.schemas.analytics import AnalyticsEventCreate
from app.schemas.response import success_response

from app.db.session import SessionLocal

router = APIRouter()

def save_event_to_db(event_data: dict, current_user_id: str | None):
    db = SessionLocal()
    try:
        db_event = AnalyticsEvent(
            session_id=event_data['session_id'],
            user_id=current_user_id,
            event_name=event_data['event_name'],
            page_url=event_data['page_url'],
            metadata_payload=event_data['metadata_payload']
        )
        db.add(db_event)
        db.commit()
    except Exception as e:
        db.rollback()
        import logging
        logging.getLogger("skinscan").error(f"Failed to save analytics event: {e}")
    finally:
        db.close()

@router.post("/track")
async def track_event(
    event: AnalyticsEventCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user)
):
    # Offload the database write to a background thread so the API responds instantly
    background_tasks.add_task(
        save_event_to_db, 
        event.model_dump(), 
        current_user.id if current_user else None
    )
    
    return success_response({"status": "tracked"})
