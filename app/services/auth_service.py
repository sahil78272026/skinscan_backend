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

    def process_google_login(self, token: str, client_id: str, consent_analysis: bool, consent_photo: bool) -> tuple[User, str]:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        from app.core.exceptions import BadRequestException
        
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)
            email = idinfo['email']
            return self.process_email_login(email, consent_analysis, consent_photo)
        except ValueError:
            raise BadRequestException("Invalid Google token")
