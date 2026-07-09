from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.services.auth_service import AuthService
from app.services.turnstile import verify_turnstile
from app.schemas.response import Envelope, success_response, error_response
from app.core.exceptions import BadRequestException
from typing import Any

router = APIRouter()

@router.post("/email", response_model=Envelope[dict[str, Any]])
async def login_email(
    request: Request,
    email: str = Form(...),
    turnstile_token: str = Form(None),
    consent_analysis: bool = Form(False),
    db: Session = Depends(get_db)
):
    # if not await verify_turnstile(turnstile_token):
    #     raise BadRequestException("Invalid CAPTCHA")
        
    auth_svc = AuthService(db)
    user, token = auth_svc.process_email_login(email, consent_analysis)
    
    return success_response({"access_token": token, "token_type": "bearer"})

@router.post("/google", response_model=Envelope[dict[str, Any]])
async def login_google(
    credential: str = Form(...),
    consent_analysis: bool = Form(False),
    db: Session = Depends(get_db)
):
    from app.config import settings
    auth_svc = AuthService(db)
    client_id = settings.google_oauth_client_id
    if not client_id:
        raise BadRequestException("Google login is not configured on the server")
        
    user, token = auth_svc.process_google_login(credential, client_id, consent_analysis)
    return success_response({"access_token": token, "token_type": "bearer"})
