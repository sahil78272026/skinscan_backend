from sqlalchemy.orm import Session
from app.models.waitlist import Waitlist
from app.schemas.waitlist import WaitlistCreate

class WaitlistRepository:
    def create(self, db: Session, obj_in: WaitlistCreate) -> Waitlist:
        waitlist = Waitlist(
            email=obj_in.email,
            analysis_id=obj_in.analysis_id,
            interest=obj_in.interest
        )
        db.add(waitlist)
        db.commit()
        db.refresh(waitlist)
        return waitlist

    def get_by_email(self, db: Session, email: str) -> Waitlist:
        return db.query(Waitlist).filter(Waitlist.email == email).first()
