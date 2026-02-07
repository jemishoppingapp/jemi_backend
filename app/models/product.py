from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)  # e.g., "fashion", "electronics"
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="category_rel")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(300), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(12, 2), nullable=False)  # Supports up to 9,999,999,999.99
    compare_at_price = Column(Numeric(12, 2), nullable=True)  # Original price for discounts
    image_url = Column(String(500), nullable=False)
    image_alt = Column(String(255), nullable=True)
    color = Column(String(50), nullable=True)
    size = Column(String(50), nullable=True)
    
    # Stock & Availability
    stock_quantity = Column(Integer, default=0)
    in_stock = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_trending = Column(Boolean, default=False)
    
    # Category
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = Column(String(100), nullable=False)  # Denormalized for quick access
    
    # Seller (for future multi-seller)
    seller_id = Column(Integer, nullable=True)  # Will link to sellers table later
    seller_name = Column(String(255), default="JEMI Store")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category_rel = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    wishlist_items = relationship("WishlistItem", back_populates="product")
