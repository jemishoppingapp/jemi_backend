import hashlib
import hmac
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.payment import (
    PaymentInitializeRequest,
    PaymentInitializeResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
)
from app.schemas.common import ApiResponse
from app.services.payment import PaymentService
from app.core.exceptions import BadRequestException

router = APIRouter()


@router.post("/initialize", response_model=ApiResponse[PaymentInitializeResponse])
def initialize_payment(
    data: PaymentInitializeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/payment/initialize
    
    Creates order from cart, calls Paystack, returns payment URL.
    Frontend redirects user to authorization_url.
    """
    service = PaymentService(db)
    result = service.initialize_payment(current_user, data)
    return ApiResponse(data=result, success=True)


@router.post("/verify", response_model=ApiResponse[PaymentVerifyResponse])
def verify_payment(
    data: PaymentVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/payment/verify
    
    Called after Paystack redirects back to frontend.
    Verifies payment with Paystack API, confirms order, deducts stock.
    """
    service = PaymentService(db)
    result = service.verify_payment(data.reference, current_user)
    return ApiResponse(data=result, success=True)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def paystack_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/payment/webhook
    
    Paystack calls this. No auth — verified by signature.
    Set this URL in Paystack Dashboard → Settings → API Keys & Webhooks.
    """
    # Verify Paystack signature
    signature = request.headers.get("x-paystack-signature", "")
    body = await request.body()
    
    expected = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
        body,
        hashlib.sha512,
    ).hexdigest()
    
    if not hmac.compare_digest(expected, signature):
        raise BadRequestException("Invalid webhook signature")
    
    import json
    payload = json.loads(body)
    
    service = PaymentService(db)
    service.handle_webhook(payload)
    
    return {"status": "ok"}