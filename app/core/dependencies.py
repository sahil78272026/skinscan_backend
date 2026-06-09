from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.config import settings
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException
from app.repositories.user_repository import UserRepository
from app.providers.base_ai import SkinAnalyzer
from app.providers.gemini_provider import GeminiAnalyzer
from app.providers.nvidia_provider import NvidiaAnalyzer
from app.providers.openrouter_provider import OpenRouterAnalyzer
from app.providers.base_storage import StorageService
from app.providers.s3_storage import S3StorageService
from app.providers.base_email import EmailService
from app.providers.resend_email import ResendEmailService
from typing import Generator

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    if not token:
        raise UnauthorizedException("Not authenticated")
    
    user_id = decode_access_token(token)
    if not user_id:
        raise UnauthorizedException("Invalid token")
        
    user_repo = UserRepository()
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise UnauthorizedException("User not found")
        
    return user

def get_analyzer() -> SkinAnalyzer:
    if settings.ai_provider == "openrouter":
        return OpenRouterAnalyzer()
    if settings.ai_provider == "nvidia":
        return NvidiaAnalyzer()
    if settings.ai_provider == "gemini":
        return GeminiAnalyzer()
    # elif settings.ai_provider == "claude": ...
    return GeminiAnalyzer()

def get_storage() -> StorageService:
    if settings.storage_provider == "r2" or settings.storage_provider == "s3":
        return S3StorageService()
    return S3StorageService()

def get_email() -> EmailService:
    if settings.email_provider == "resend":
        return ResendEmailService()
    return ResendEmailService()
