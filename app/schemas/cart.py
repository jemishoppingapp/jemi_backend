from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


class CartItemResponse(BaseModel):
    """Matches frontend CartItem interface"""
    id: int
    productId: int
    name: str
    price: float
    originalPrice: Optional[float] = None
    image: str
    quantity: int
    stock: int
    seller: str
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_model(cls, cart_item) -> "CartItemResponse":
        product = cart_item.product
        return cls(
            id=cart_item.id,
            productId=product.id,
            name=product.name,
            price=float(product.price),
            originalPrice=float(product.compare_at_price) if product.compare_at_price else None,
            image=product.image_url,
            quantity=cart_item.quantity,
            stock=product.stock_quantity,
            seller=product.seller_name,
        )


class CartResponse(BaseModel):
    """Full cart response"""
    id: int
    items: list[CartItemResponse]
    itemCount: int
    subtotal: float
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_model(cls, cart) -> "CartResponse":
        items = [CartItemResponse.from_orm_model(item) for item in cart.items]
        subtotal = sum(item.price * item.quantity for item in items)
        return cls(
            id=cart.id,
            items=items,
            itemCount=sum(item.quantity for item in items),
            subtotal=subtotal,
        )


class AddToCartRequest(BaseModel):
    """Request to add item to cart"""
    product_id: int = Field(..., alias="productId")
    quantity: int = Field(1, ge=1)
    
    class Config:
        populate_by_name = True
