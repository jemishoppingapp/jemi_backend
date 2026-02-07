from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse, OrderListResponse
from app.schemas.common import ApiResponse
from app.services.order import OrderService

router = APIRouter()


@router.get("", response_model=ApiResponse[OrderListResponse])
def get_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user's orders with pagination.
    
    - GET /api/v1/orders
    - Matches frontend: ENDPOINTS.ORDERS.BASE
    
    Query params:
    - page: Page number
    - limit: Items per page
    - status: Filter by order status
    """
    service = OrderService(db)
    result = service.get_orders(
        user=current_user,
        page=page,
        limit=limit,
        status=status,
    )
    return ApiResponse(data=result, success=True)


@router.post("", response_model=ApiResponse[OrderResponse], status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create new order from cart.
    
    - POST /api/v1/orders
    - Matches frontend: ENDPOINTS.ORDERS.BASE
    
    This will:
    1. Validate cart items and stock
    2. Create order with items
    3. Update product stock
    4. Clear user's cart
    5. Generate pickup code
    """
    service = OrderService(db)
    result = service.create_order(user=current_user, data=data)
    return ApiResponse(data=result, message="Order placed successfully", success=True)


@router.get("/{order_id}", response_model=ApiResponse[OrderResponse])
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get single order details.
    
    - GET /api/v1/orders/{id}
    - Matches frontend: ENDPOINTS.ORDERS.DETAIL(id)
    """
    service = OrderService(db)
    result = service.get_order(user=current_user, order_id=order_id)
    return ApiResponse(data=result, success=True)


@router.post("/{order_id}/cancel", response_model=ApiResponse[OrderResponse])
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cancel an order.
    
    - POST /api/v1/orders/{id}/cancel
    - Matches frontend: ENDPOINTS.ORDERS.CANCEL(id)
    
    Only pending or confirmed orders can be cancelled.
    Stock will be restored to products.
    """
    service = OrderService(db)
    result = service.cancel_order(user=current_user, order_id=order_id)
    return ApiResponse(data=result, message="Order cancelled", success=True)


@router.get("/{order_id}/track", response_model=ApiResponse[OrderResponse])
def track_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Track order status with timeline.
    
    - GET /api/v1/orders/{id}/track
    - Matches frontend: ENDPOINTS.ORDERS.TRACK(id)
    """
    service = OrderService(db)
    result = service.get_order(user=current_user, order_id=order_id)
    return ApiResponse(data=result, success=True)
