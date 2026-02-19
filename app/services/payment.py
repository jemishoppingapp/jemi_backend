import httpx
import logging
from sqlalchemy.orm import Session

from app.config import settings
from app.models.order import Order, OrderItem, OrderTimeline, OrderStatus, PaymentStatus
from app.models.cart import Cart, CartItem
from app.models.user import User
from app.schemas.payment import (
    PaymentInitializeRequest,
    PaymentInitializeResponse,
    PaymentVerifyResponse,
)
from app.core.exceptions import BadRequestException, PaymentFailedException, NotFoundException, InsufficientStockException
from app.core.validators import generate_order_number, generate_pickup_code

logger = logging.getLogger(__name__)

PAYSTACK_BASE_URL = "https://api.paystack.co"


class PaymentService:
    """Paystack payment integration service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _paystack_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
    
    def initialize_payment(
        self, user: User, data: PaymentInitializeRequest
    ) -> PaymentInitializeResponse:
        """
        1. Validate cart & stock
        2. Create PENDING order
        3. Call Paystack to get payment URL
        4. Return URL to frontend
        """
        # Get cart
        cart = self.db.query(Cart).filter(Cart.user_id == user.id).first()
        if not cart or not cart.items:
            raise BadRequestException("Cart is empty")
        
        if not user.profile_completed:
            raise BadRequestException("Complete your profile before checkout")
        
        # Validate stock & calculate total
        order_items_data = []
        subtotal = 0
        
        for cart_item in cart.items:
            product = cart_item.product
            if not product.is_active:
                raise BadRequestException(f"'{product.name}' is no longer available")
            if product.stock_quantity < cart_item.quantity:
                raise InsufficientStockException(
                    product.name, product.stock_quantity, cart_item.quantity
                )
            item_total = float(product.price) * cart_item.quantity
            subtotal += item_total
            order_items_data.append({
                "product": product,
                "quantity": cart_item.quantity,
                "unit_price": float(product.price),
                "total_price": item_total,
            })
        
        # Create order (PENDING)
        order = Order(
            user_id=user.id,
            order_number=generate_order_number(),
            subtotal=subtotal,
            delivery_fee=0,
            total=subtotal,
            status=OrderStatus.PENDING.value,
            payment_status=PaymentStatus.PENDING.value,
            payment_method="paystack",
            pickup_location=data.pickup_location,
            pickup_code=generate_pickup_code(),
            customer_name=user.nickname or user.name,
            customer_phone=user.phone,
            customer_email=user.email,
            customer_note=data.customer_note,
        )
        self.db.add(order)
        self.db.flush()
        
        # Create order items (stock not deducted yet — only on verify)
        for item_data in order_items_data:
            product = item_data["product"]
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                product_image=product.image_url,
                unit_price=item_data["unit_price"],
                quantity=item_data["quantity"],
                total_price=item_data["total_price"],
            )
            self.db.add(order_item)
        
        # Timeline
        self.db.add(OrderTimeline(
            order_id=order.id,
            status=OrderStatus.PENDING.value,
            note="Order created, awaiting payment",
        ))
        
        self.db.commit()
        self.db.refresh(order)
        
        # Call Paystack
        amount_kobo = int(subtotal * 100)  # Paystack uses kobo
        reference = f"JEMI-{order.order_number}"
        
        payload = {
            "email": user.email,
            "amount": amount_kobo,
            "reference": reference,
            "callback_url": f"{settings.FRONTEND_URL}/checkout/verify",
            "metadata": {
                "order_id": order.id,
                "order_number": order.order_number,
                "customer_name": user.nickname or user.name,
                "pickup_location": data.pickup_location,
            },
        }
        
        with httpx.Client() as client:
            resp = client.post(
                f"{PAYSTACK_BASE_URL}/transaction/initialize",
                json=payload,
                headers=self._paystack_headers(),
                timeout=30,
            )
        
        if resp.status_code != 200:
            logger.error(f"Paystack init failed: {resp.text}")
            raise PaymentFailedException("Could not initialize payment")
        
        result = resp.json()
        if not result.get("status"):
            raise PaymentFailedException(result.get("message", "Payment init failed"))
        
        ps_data = result["data"]
        return PaymentInitializeResponse(
            authorization_url=ps_data["authorization_url"],
            access_code=ps_data["access_code"],
            reference=ps_data["reference"],
        )
    
    def verify_payment(self, reference: str, user: User) -> PaymentVerifyResponse:
        """
        Called after Paystack redirects back.
        Verify with Paystack API, confirm order, deduct stock, clear cart.
        """
        # Call Paystack verify
        with httpx.Client() as client:
            resp = client.get(
                f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}",
                headers=self._paystack_headers(),
                timeout=30,
            )
        
        if resp.status_code != 200:
            raise PaymentFailedException("Payment verification failed")
        
        result = resp.json()
        if not result.get("status"):
            raise PaymentFailedException("Payment not verified")
        
        ps_data = result["data"]
        
        if ps_data["status"] != "success":
            raise PaymentFailedException(f"Payment status: {ps_data['status']}")
        
        # Find order by reference
        order_number = reference.replace("JEMI-", "")
        order = self.db.query(Order).filter(
            Order.order_number == order_number,
            Order.user_id == user.id,
        ).first()
        
        if not order:
            raise NotFoundException("Order", order_number)
        
        if order.payment_status == PaymentStatus.PAID.value:
            # Already verified (idempotent)
            return PaymentVerifyResponse(
                order_number=order.order_number,
                pickup_code=order.pickup_code,
                pickup_location=order.pickup_location or "",
                total=f"₦{float(order.total):,.0f}",
                status="success",
            )
        
        # Verify amount matches
        expected_kobo = int(float(order.total) * 100)
        if ps_data["amount"] != expected_kobo:
            logger.error(
                f"Amount mismatch: expected {expected_kobo}, got {ps_data['amount']}"
            )
            raise PaymentFailedException("Payment amount mismatch")
        
        # Confirm order
        order.payment_status = PaymentStatus.PAID.value
        order.status = OrderStatus.CONFIRMED.value
        
        # Deduct stock
        for item in order.items:
            if item.product:
                item.product.stock_quantity -= item.quantity
                if item.product.stock_quantity <= 0:
                    item.product.in_stock = False
        
        # Timeline
        self.db.add(OrderTimeline(
            order_id=order.id,
            status=OrderStatus.CONFIRMED.value,
            note=f"Payment confirmed via Paystack (ref: {reference})",
        ))
        
        # Clear cart
        cart = self.db.query(Cart).filter(Cart.user_id == user.id).first()
        if cart:
            self.db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        
        self.db.commit()
        self.db.refresh(order)
        
        return PaymentVerifyResponse(
            order_number=order.order_number,
            pickup_code=order.pickup_code,
            pickup_location=order.pickup_location or "",
            total=f"₦{float(order.total):,.0f}",
            status="success",
        )
    
    def handle_webhook(self, payload: dict) -> None:
        """
        Handle Paystack webhook (backup verification).
        Called by Paystack servers — no user auth.
        """
        event = payload.get("event")
        data = payload.get("data", {})
        
        if event == "charge.success":
            reference = data.get("reference", "")
            order_number = reference.replace("JEMI-", "")
            
            order = self.db.query(Order).filter(
                Order.order_number == order_number
            ).first()
            
            if not order:
                logger.warning(f"Webhook: order not found for ref {reference}")
                return
            
            if order.payment_status == PaymentStatus.PAID.value:
                return  # Already processed
            
            # Confirm payment
            order.payment_status = PaymentStatus.PAID.value
            order.status = OrderStatus.CONFIRMED.value
            
            for item in order.items:
                if item.product:
                    item.product.stock_quantity -= item.quantity
                    if item.product.stock_quantity <= 0:
                        item.product.in_stock = False
            
            self.db.add(OrderTimeline(
                order_id=order.id,
                status=OrderStatus.CONFIRMED.value,
                note=f"Payment confirmed via webhook (ref: {reference})",
            ))
            
            # Clear cart
            cart = self.db.query(Cart).filter(Cart.user_id == order.user_id).first()
            if cart:
                self.db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
            
            self.db.commit()
            logger.info(f"Webhook: order {order_number} confirmed")