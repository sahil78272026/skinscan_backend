from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.core.security import create_access_token
from app.models.user import User

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository()

    def process_email_login(self, email: str, consent_analysis: bool, consent_photo: bool) -> tuple[User, str]:
        user = self.repo.get_by_email(self.db, email)
        if not user:
            user_in = UserCreate(
                email=email,
                consent_analysis=consent_analysis,
                consent_photo_storage=consent_photo
            )
            user = self.repo.create(self.db, user_in)
        else:
            # Update consents if they are provided
            updates = {}
            if consent_analysis:
                updates["consent_analysis"] = consent_analysis
            if consent_photo:
                updates["consent_photo_storage"] = consent_photo
            if updates:
                user = self.repo.update(self.db, user, updates)

        token = create_access_token(subject=str(user.id))
        return user, token
