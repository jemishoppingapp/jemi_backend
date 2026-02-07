from pydantic import BaseModel
from datetime import datetime
from app.schemas.product import ProductResponse


class WishlistItemCreate(BaseModel):
    product_id: int


class WishlistItemResponse(BaseModel):
    """Matches frontend WishlistItem"""
    id: str
    productId: str
    addedAt: str
    product: ProductResponse
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_model(cls, wishlist_item) -> "WishlistItemResponse":
        return cls(
            id=str(wishlist_item.id),
            productId=str(wishlist_item.product_id),
            addedAt=wishlist_item.added_at.isoformat(),
            product=ProductResponse.from_orm_model(wishlist_item.product),
        )


class WishlistResponse(BaseModel):
    """Full wishlist response"""
    items: list[WishlistItemResponse]
    total: int
