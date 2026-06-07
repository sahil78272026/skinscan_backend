from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.waitlist import WaitlistCreate, WaitlistOut
from app.schemas.response import Envelope, success_response
from app.repositories.waitlist_repository import WaitlistRepository

router = APIRouter()

@router.post("/", response_model=Envelope[WaitlistOut])
async def join_waitlist(
    req: WaitlistCreate,
    db: Session = Depends(get_db)
):
    repo = WaitlistRepository()
    waitlist = repo.get_by_email(db, req.email)
    if not waitlist:
        waitlist = repo.create(db, req)
    return success_response(WaitlistOut.model_validate(waitlist))
