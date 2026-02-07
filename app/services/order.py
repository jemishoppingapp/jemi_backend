from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone

from app.models.order import Order, OrderItem, OrderTimeline, OrderStatus, PaymentStatus
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse, OrderListResponse
from app.core.exceptions import NotFoundException, BadRequestException, InsufficientStockException
from app.core.validators import generate_order_number, generate_pickup_code


class OrderService:
    """Service for order operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_order(self, user: User, data: OrderCreate) -> OrderResponse:
        """Create a new order from cart items."""
        # Get user's cart
        cart = self.db.query(Cart).filter(Cart.user_id == user.id).first()
        
        if not cart or not cart.items:
            raise BadRequestException("Cart is empty")
        
        # Validate stock for all items
        order_items_data = []
        subtotal = 0
        
        for cart_item in cart.items:
            product = cart_item.product
            
            if not product.is_active:
                raise BadRequestException(f"Product '{product.name}' is no longer available")
            
            if product.stock_quantity < cart_item.quantity:
                raise InsufficientStockException(
                    product.name,
                    product.stock_quantity,
                    cart_item.quantity,
                )
            
            item_total = float(product.price) * cart_item.quantity
            subtotal += item_total
            
            order_items_data.append({
                "product": product,
                "quantity": cart_item.quantity,
                "unit_price": float(product.price),
                "total_price": item_total,
            })
        
        # Create order
        order = Order(
            user_id=user.id,
            order_number=generate_order_number(),
            subtotal=subtotal,
            delivery_fee=0,  # Pickup model - no delivery fee
            total=subtotal,
            status=OrderStatus.PENDING.value,
            payment_status=PaymentStatus.PENDING.value,
            payment_method=data.payment_method,
            pickup_location=data.pickup_location,
            pickup_code=generate_pickup_code(),
            customer_name=user.name,
            customer_phone=user.phone,
            customer_email=user.email,
            customer_note=data.customer_note,
        )
        
        self.db.add(order)
        self.db.flush()
        
        # Create order items and update stock
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
            
            # Update product stock
            product.stock_quantity -= item_data["quantity"]
            if product.stock_quantity <= 0:
                product.in_stock = False
        
        # Create initial timeline entry
        timeline = OrderTimeline(
            order_id=order.id,
            status=OrderStatus.PENDING.value,
            note="Order placed successfully",
        )
        self.db.add(timeline)
        
        # Clear cart
        self.db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        
        self.db.commit()
        self.db.refresh(order)
        
        return OrderResponse.from_orm_model(order, include_details=True)
    
    def get_order(self, user: User, order_id: int) -> OrderResponse:
        """Get single order by ID."""
        order = self.db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user.id,
        ).first()
        
        if not order:
            raise NotFoundException("Order", order_id)
        
        return OrderResponse.from_orm_model(order, include_details=True)
    
    def get_orders(
        self,
        user: User,
        page: int = 1,
        limit: int = 10,
        status: Optional[str] = None,
    ) -> OrderListResponse:
        """Get user's orders with pagination."""
        query = self.db.query(Order).filter(Order.user_id == user.id)
        
        if status:
            query = query.filter(Order.status == status)
        
        query = query.order_by(Order.created_at.desc())
        
        # Get total count
        total = query.count()
        
        # Paginate
        offset = (page - 1) * limit
        orders = query.offset(offset).limit(limit).all()
        
        order_responses = [OrderResponse.from_orm_model(o) for o in orders]
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        
        return OrderListResponse(
            orders=order_responses,
            total=total,
            page=page,
            limit=limit,
            totalPages=total_pages,
        )
    
    def cancel_order(self, user: User, order_id: int) -> OrderResponse:
        """Cancel an order."""
        order = self.db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user.id,
        ).first()
        
        if not order:
            raise NotFoundException("Order", order_id)
        
        # Can only cancel pending or confirmed orders
        if order.status not in [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]:
            raise BadRequestException(
                f"Cannot cancel order with status '{order.status}'"
            )
        
        # Restore stock
        for item in order.items:
            if item.product:
                item.product.stock_quantity += item.quantity
                item.product.in_stock = True
        
        # Update order status
        order.status = OrderStatus.CANCELLED.value
        
        # Add timeline entry
        timeline = OrderTimeline(
            order_id=order.id,
            status=OrderStatus.CANCELLED.value,
            note="Order cancelled by customer",
        )
        self.db.add(timeline)
        
        self.db.commit()
        self.db.refresh(order)
        
        return OrderResponse.from_orm_model(order, include_details=True)
    
    def update_order_status(
        self,
        order_id: int,
        new_status: str,
        note: Optional[str] = None,
    ) -> OrderResponse:
        """Update order status (admin/seller only)."""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            raise NotFoundException("Order", order_id)
        
        order.status = new_status
        
        if new_status == OrderStatus.COMPLETED.value:
            order.completed_at = datetime.now(timezone.utc)
        
        # Add timeline entry
        timeline = OrderTimeline(
            order_id=order.id,
            status=new_status,
            note=note,
        )
        self.db.add(timeline)
        
        self.db.commit()
        self.db.refresh(order)
        
        return OrderResponse.from_orm_model(order, include_details=True)
