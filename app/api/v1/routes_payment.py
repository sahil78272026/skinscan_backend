from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.response import Envelope, success_response, error_response
from app.services.payment_service import payment_service
from app.core.exceptions import BadRequestException
from app.config import settings
from pydantic import BaseModel
import hmac
import hashlib

router = APIRouter()

class OrderCreateRequest(BaseModel):
    plan_id: str  # e.g., 'yearly', 'lifetime'

@router.post("/create-order", response_model=Envelope[dict])
async def create_order(
    request: OrderCreateRequest,
    current_user: User = Depends(get_current_user)
):
    if request.plan_id == "yearly":
        amount = 800  # ₹800
    elif request.plan_id == "lifetime":
        amount = 1200 # ₹1200
    else:
        raise BadRequestException("Invalid plan ID")

    receipt_id = f"receipt_{current_user.id.hex[:10]}"
    try:
        order = payment_service.create_order(amount, receipt_id)
        return success_response({
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key_id": settings.razorpay_key_id
        })
    except Exception as e:
        raise BadRequestException(f"Failed to create order: {str(e)}")

@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    payload_body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature")

    if not signature:
        return error_response("Missing signature", 400)

    # Verify Webhook Signature
    secret = settings.razorpay_webhook_secret.encode('utf-8')
    expected_signature = hmac.new(secret, payload_body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        return error_response("Invalid signature", 400)

    payload = await request.json()
    
    # Process successful payment
    if payload.get("event") == "payment.captured":
        payment_entity = payload["payload"]["payment"]["entity"]
        user_email = payment_entity.get("email")
        amount = payment_entity.get("amount") # in paise
        
        if user_email:
            user = db.query(User).filter(User.email == user_email).first()
            if user:
                # Upgrade user
                if amount >= 120000: # ₹1200
                    user.subscription_tier = "lifetime"
                else:
                    user.subscription_tier = "yearly"
                db.commit()

    return {"status": "ok"}

class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    plan_id: str

@router.post("/verify-payment", response_model=Envelope[bool])
async def verify_payment(
    request: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        payment_service.verify_signature(
            request.razorpay_order_id,
            request.razorpay_payment_id,
            request.razorpay_signature
        )
        
        # Upgrade user
        current_user.subscription_tier = request.plan_id
        db.commit()
        return success_response(True)
    except Exception as e:
        raise BadRequestException(f"Payment verification failed: {str(e)}")
