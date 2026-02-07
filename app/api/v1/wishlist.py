from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.wishlist import WishlistItem
from app.models.product import Product
from app.schemas.wishlist import WishlistItemCreate, WishlistItemResponse, WishlistResponse
from app.schemas.common import ApiResponse
from app.core.exceptions import NotFoundException, ConflictException

router = APIRouter()


@router.get("", response_model=ApiResponse[WishlistResponse])
def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user's wishlist.
    
    - GET /api/v1/wishlist
    - Matches frontend: ENDPOINTS.WISHLIST.BASE
    """
    items = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id
    ).all()
    
    item_responses = [WishlistItemResponse.from_orm_model(item) for item in items]
    
    return ApiResponse(
        data=WishlistResponse(items=item_responses, total=len(item_responses)),
        success=True,
    )


@router.post("", response_model=ApiResponse[WishlistItemResponse], status_code=status.HTTP_201_CREATED)
def add_to_wishlist(
    data: WishlistItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add item to wishlist.
    
    - POST /api/v1/wishlist
    - Matches frontend: ENDPOINTS.WISHLIST.BASE
    """
    # Check product exists
    product = db.query(Product).filter(
        Product.id == data.product_id,
        Product.is_active == True,
    ).first()
    
    if not product:
        raise NotFoundException("Product", data.product_id)
    
    # Check if already in wishlist
    existing = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.product_id == data.product_id,
    ).first()
    
    if existing:
        raise ConflictException("Item already in wishlist")
    
    # Add to wishlist
    wishlist_item = WishlistItem(
        user_id=current_user.id,
        product_id=data.product_id,
    )
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)
    
    return ApiResponse(
        data=WishlistItemResponse.from_orm_model(wishlist_item),
        message="Added to wishlist",
        success=True,
    )


@router.delete("/items/{item_id}", response_model=ApiResponse[dict])
def remove_from_wishlist(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove item from wishlist.
    
    - DELETE /api/v1/wishlist/items/{id}
    - Matches frontend: ENDPOINTS.WISHLIST.ITEM(id)
    """
    wishlist_item = db.query(WishlistItem).filter(
        WishlistItem.id == item_id,
        WishlistItem.user_id == current_user.id,
    ).first()
    
    if not wishlist_item:
        raise NotFoundException("Wishlist item", item_id)
    
    db.delete(wishlist_item)
    db.commit()
    
    return ApiResponse(
        data={"deleted": True},
        message="Removed from wishlist",
        success=True,
    )
