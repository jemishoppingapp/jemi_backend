from sqlalchemy.orm import Session
from typing import Optional

from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import CartResponse, CartItemResponse
from app.core.exceptions import NotFoundException, BadRequestException, InsufficientStockException


class CartService:
    """Service for cart operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_cart(self, user: User) -> Cart:
        """Get user's cart or create if doesn't exist."""
        cart = self.db.query(Cart).filter(Cart.user_id == user.id).first()
        
        if not cart:
            cart = Cart(user_id=user.id)
            self.db.add(cart)
            self.db.commit()
            self.db.refresh(cart)
        
        return cart
    
    def get_cart(self, user: User) -> CartResponse:
        """Get user's cart with items."""
        cart = self.get_or_create_cart(user)
        return CartResponse.from_orm_model(cart)
    
    def add_item(self, user: User, product_id: int, quantity: int = 1) -> CartResponse:
        """Add item to cart."""
        cart = self.get_or_create_cart(user)
        
        # Check product exists and is available
        product = self.db.query(Product).filter(
            Product.id == product_id,
            Product.is_active == True,
        ).first()
        
        if not product:
            raise NotFoundException("Product", product_id)
        
        if not product.in_stock or product.stock_quantity < quantity:
            raise InsufficientStockException(
                product.name,
                product.stock_quantity,
                quantity,
            )
        
        # Check if item already in cart
        existing_item = self.db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
        ).first()
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + quantity
            if new_quantity > product.stock_quantity:
                raise InsufficientStockException(
                    product.name,
                    product.stock_quantity,
                    new_quantity,
                )
            existing_item.quantity = new_quantity
        else:
            # Add new item
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
            )
            self.db.add(cart_item)
        
        self.db.commit()
        self.db.refresh(cart)
        
        return CartResponse.from_orm_model(cart)
    
    def update_item_quantity(
        self,
        user: User,
        item_id: int,
        quantity: int,
    ) -> CartResponse:
        """Update cart item quantity."""
        cart = self.get_or_create_cart(user)
        
        cart_item = self.db.query(CartItem).filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id,
        ).first()
        
        if not cart_item:
            raise NotFoundException("Cart item", item_id)
        
        if quantity <= 0:
            # Remove item if quantity is 0 or less
            self.db.delete(cart_item)
        else:
            # Check stock
            if cart_item.product.stock_quantity < quantity:
                raise InsufficientStockException(
                    cart_item.product.name,
                    cart_item.product.stock_quantity,
                    quantity,
                )
            cart_item.quantity = quantity
        
        self.db.commit()
        self.db.refresh(cart)
        
        return CartResponse.from_orm_model(cart)
    
    def remove_item(self, user: User, item_id: int) -> CartResponse:
        """Remove item from cart."""
        cart = self.get_or_create_cart(user)
        
        cart_item = self.db.query(CartItem).filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id,
        ).first()
        
        if not cart_item:
            raise NotFoundException("Cart item", item_id)
        
        self.db.delete(cart_item)
        self.db.commit()
        self.db.refresh(cart)
        
        return CartResponse.from_orm_model(cart)
    
    def clear_cart(self, user: User) -> CartResponse:
        """Remove all items from cart."""
        cart = self.get_or_create_cart(user)
        
        self.db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        self.db.commit()
        self.db.refresh(cart)
        
        return CartResponse.from_orm_model(cart)
