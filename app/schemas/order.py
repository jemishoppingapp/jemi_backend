from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    READY_FOR_PICKUP = "ready_for_pickup"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


# ============ Order Item Schemas ============

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)


class OrderItemResponse(BaseModel):
    """Matches frontend OrderItem"""
    id: int
    name: str
    price: str  # Formatted
    imageSrc: str
    imageAlt: str
    description: Optional[str] = None
    quantity: int
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_model(cls, order_item) -> "OrderItemResponse":
        return cls(
            id=order_item.id,
            name=order_item.product_name,
            price=f"₦{float(order_item.unit_price):,.0f}",
            imageSrc=order_item.product_image or "",
            imageAlt=order_item.product_name,
            description=None,  # Could add product description if needed
            quantity=order_item.quantity,
        )


# ============ Order Timeline Schemas ============

class OrderTimelineResponse(BaseModel):
    """Matches frontend OrderTimeline"""
    status: str
    timestamp: str
    note: Optional[str] = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_model(cls, timeline) -> "OrderTimelineResponse":
        return cls(
            status=timeline.status,
            timestamp=timeline.created_at.isoformat(),
            note=timeline.note,
        )


# ============ Order Schemas ============

class OrderCreate(BaseModel):
    """Matches frontend CreateOrderData"""
    items: list[OrderItemBase]
    pickup_location: Optional[str] = Field(None, alias="shippingAddressId")
    payment_method: str = Field(..., alias="paymentMethod")
    customer_note: Optional[str] = None
    
    class Config:
        populate_by_name = True


class OrderResponse(BaseModel):
    """Matches frontend Order interface"""
    id: str
    orderNumber: str
    datePlaced: str
    dateDelivered: Optional[str] = None
    totalAmount: str
    status: str
    items: list[OrderItemResponse]
    
    # Extended fields
    subtotal: Optional[float] = None
    deliveryFee: Optional[float] = None
    total: Optional[float] = None
    paymentStatus: Optional[str] = None
    paymentMethod: Optional[str] = None
    pickupLocation: Optional[str] = None
    pickupCode: Optional[str] = None
    timeline: list[OrderTimelineResponse] = []
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_model(cls, order, include_details: bool = False) -> "OrderResponse":
        items = [OrderItemResponse.from_orm_model(item) for item in order.items]
        
        response = cls(
            id=str(order.id),
            orderNumber=order.order_number,
            datePlaced=order.created_at.strftime("%b %d, %Y"),
            dateDelivered=order.completed_at.strftime("%b %d, %Y") if order.completed_at else None,
            totalAmount=f"₦{float(order.total):,.0f}",
            status=order.status,
            items=items,
        )
        
        if include_details:
            response.subtotal = float(order.subtotal)
            response.deliveryFee = float(order.delivery_fee)
            response.total = float(order.total)
            response.paymentStatus = order.payment_status
            response.paymentMethod = order.payment_method
            response.pickupLocation = order.pickup_location
            response.pickupCode = order.pickup_code
            response.timeline = [
                OrderTimelineResponse.from_orm_model(t) for t in order.timeline
            ]
        
        return response


class OrderListResponse(BaseModel):
    """Matches frontend OrdersResponse"""
    orders: list[OrderResponse]
    total: int
    page: int
    limit: int
    totalPages: int
