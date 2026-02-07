from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import User
from app.models.cart import Cart
from app.schemas.user import RegisterData, AuthResponse, UserResponse
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import UnauthorizedException, ConflictException, BadRequestException
from app.core.validators import normalize_phone


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register(self, data: RegisterData) -> AuthResponse:
        """Register a new user."""
        # Check if email already exists
        if self.db.query(User).filter(User.email == data.email.lower()).first():
            raise ConflictException("Email already registered")
        
        # Normalize and check phone
        normalized_phone = normalize_phone(data.phone)
        if self.db.query(User).filter(User.phone == normalized_phone).first():
            raise ConflictException("Phone number already registered")
        
        # Create user
        user = User(
            email=data.email.lower(),
            phone=normalized_phone,
            name=data.name,
            hashed_password=hash_password(data.password),
        )
        
        self.db.add(user)
        self.db.flush()  # Get the user ID
        
        # Create empty cart for user
        cart = Cart(user_id=user.id)
        self.db.add(cart)
        
        self.db.commit()
        self.db.refresh(user)
        
        # Generate tokens
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            token=access_token,
            refresh_token=refresh_token,
        )
    
    def login(self, email: str, password: str) -> AuthResponse:
        """Authenticate user and return tokens."""
        user = self.db.query(User).filter(User.email == email.lower()).first()
        
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")
        
        if not user.is_active:
            raise UnauthorizedException("Account is disabled")
        
        # Generate tokens
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            token=access_token,
            refresh_token=refresh_token,
        )
    
    def refresh_tokens(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token."""
        payload = decode_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")
        
        user_id = payload.get("sub")
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or disabled")
        
        # Generate new tokens
        token_data = {"sub": str(user.id), "email": user.email}
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)
        
        return {
            "token": new_access_token,
            "refresh_token": new_refresh_token,
        }
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email.lower()).first()
