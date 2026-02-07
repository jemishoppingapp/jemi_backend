from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.cart import CartResponse, AddToCartRequest, CartItemUpdate
from app.schemas.common import ApiResponse
from app.services.cart import CartService

router = APIRouter()


@router.get("", response_model=ApiResponse[CartResponse])
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current user's cart.
    
    - GET /api/v1/cart
    - Matches frontend: ENDPOINTS.CART.BASE
    """
    service = CartService(db)
    result = service.get_cart(current_user)
    return ApiResponse(data=result, success=True)


@router.post("/items", response_model=ApiResponse[CartResponse])
def add_to_cart(
    data: AddToCartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add item to cart.
    
    - POST /api/v1/cart/items
    - Matches frontend: ENDPOINTS.CART.ITEMS
    """
    service = CartService(db)
    result = service.add_item(
        user=current_user,
        product_id=data.product_id,
        quantity=data.quantity,
    )
    return ApiResponse(data=result, message="Item added to cart", success=True)


@router.put("/items/{item_id}", response_model=ApiResponse[CartResponse])
def update_cart_item(
    item_id: int,
    data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update cart item quantity.
    
    - PUT /api/v1/cart/items/{id}
    - Matches frontend: ENDPOINTS.CART.ITEM(id)
    """
    service = CartService(db)
    result = service.update_item_quantity(
        user=current_user,
        item_id=item_id,
        quantity=data.quantity,
    )
    return ApiResponse(data=result, message="Cart updated", success=True)


@router.delete("/items/{item_id}", response_model=ApiResponse[CartResponse])
def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove item from cart.
    
    - DELETE /api/v1/cart/items/{id}
    - Matches frontend: ENDPOINTS.CART.ITEM(id)
    """
    service = CartService(db)
    result = service.remove_item(user=current_user, item_id=item_id)
    return ApiResponse(data=result, message="Item removed from cart", success=True)


@router.delete("/clear", response_model=ApiResponse[CartResponse])
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Clear all items from cart.
    
    - DELETE /api/v1/cart/clear
    - Matches frontend: ENDPOINTS.CART.CLEAR
    """
    service = CartService(db)
    result = service.clear_cart(current_user)
    return ApiResponse(data=result, message="Cart cleared", success=True)
