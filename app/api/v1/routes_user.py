from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db, get_storage
from app.models.user import User
from app.schemas.user import UserOut, DeleteDataRequest
from app.schemas.response import Envelope, success_response
from app.repositories.user_repository import UserRepository
from app.repositories.analysis_repository import AnalysisRepository
from app.providers.base_storage import StorageService

router = APIRouter()

@router.get("/me", response_model=Envelope[UserOut])
async def get_me(current_user: User = Depends(get_current_user)):
    return success_response(UserOut.model_validate(current_user))

@router.delete("/me/data", response_model=Envelope[bool])
async def delete_my_data(
    req: DeleteDataRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage)
):
    if not req.confirm:
        return success_response(False)
        
    analysis_repo = AnalysisRepository()
    analyses = analysis_repo.get_by_user(db, current_user.id)
    
    # Delete photos from storage
    for a in analyses:
        if a.photo_object_key:
            await storage.delete(a.photo_object_key)
            
    # Delete user (cascade will delete analyses if configured, or delete explicitly)
    user_repo = UserRepository()
    user_repo.delete(db, current_user.id)
    
    return success_response(True)
