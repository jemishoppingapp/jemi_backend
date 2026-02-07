from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    READY_FOR_PICKUP = "ready_for_pickup"  # JEMI uses pickup model
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    order_number = Column(String(20), unique=True, index=True, nullable=False)
    
    # Pricing
    subtotal = Column(Numeric(12, 2), nullable=False)
    delivery_fee = Column(Numeric(12, 2), default=0)  # Usually 0 for pickup
    total = Column(Numeric(12, 2), nullable=False)
    
    # Status
    status = Column(String(50), default=OrderStatus.PENDING.value, nullable=False)
    payment_status = Column(String(50), default=PaymentStatus.PENDING.value, nullable=False)
    payment_method = Column(String(50), nullable=True)  # "cash_on_pickup", "transfer", etc.
    
    # Pickup Details
    pickup_location = Column(String(500), nullable=True)  # Campus location
    pickup_code = Column(String(10), nullable=True)  # Verification code for pickup
    
    # Contact (denormalized for order history)
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(255), nullable=True)
    
    # Notes
    customer_note = Column(Text, nullable=True)
    seller_note = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    timeline = relationship("OrderTimeline", back_populates="order", cascade="all, delete-orphan", order_by="OrderTimeline.created_at")


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    
    # Snapshot of product at time of order (prices can change)
    product_name = Column(String(255), nullable=False)
    product_image = Column(String(500), nullable=True)
    unit_price = Column(Numeric(12, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)  # unit_price * quantity
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class OrderTimeline(Base):
    __tablename__ = "order_timeline"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False)
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="timeline")
