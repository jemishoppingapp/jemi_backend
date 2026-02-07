from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import User, Address
from app.schemas.user import UserResponse, UserUpdate, AddressCreate, AddressResponse
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.validators import normalize_phone


class UserService:
    """Service for user profile operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_profile(self, user: User) -> UserResponse:
        """Get user profile."""
        return UserResponse.model_validate(user)
    
    def update_profile(self, user: User, data: UserUpdate) -> UserResponse:
        """Update user profile."""
        if data.name is not None:
            user.name = data.name
        
        if data.phone is not None:
            normalized_phone = normalize_phone(data.phone)
            # Check if phone is already used by another user
            existing = self.db.query(User).filter(
                User.phone == normalized_phone,
                User.id != user.id,
            ).first()
            if existing:
                raise BadRequestException("Phone number already in use")
            user.phone = normalized_phone
        
        if data.avatar is not None:
            user.avatar = data.avatar
        
        self.db.commit()
        self.db.refresh(user)
        
        return UserResponse.model_validate(user)
    
    # ============ Address Operations ============
    
    def get_addresses(self, user: User) -> list[AddressResponse]:
        """Get all user addresses."""
        return [AddressResponse.model_validate(a) for a in user.addresses]
    
    def add_address(self, user: User, data: AddressCreate) -> AddressResponse:
        """Add new address."""
        # If this is the first address or marked as default, make it default
        if data.is_default or not user.addresses:
            # Unset other defaults
            for addr in user.addresses:
                addr.is_default = False
        
        address = Address(
            user_id=user.id,
            label=data.label,
            street=data.street,
            city=data.city,
            state=data.state,
            landmark=data.landmark,
            is_default=data.is_default or not user.addresses,
        )
        
        self.db.add(address)
        self.db.commit()
        self.db.refresh(address)
        
        return AddressResponse.model_validate(address)
    
    def update_address(
        self,
        user: User,
        address_id: int,
        data: AddressCreate,
    ) -> AddressResponse:
        """Update existing address."""
        address = self.db.query(Address).filter(
            Address.id == address_id,
            Address.user_id == user.id,
        ).first()
        
        if not address:
            raise NotFoundException("Address", address_id)
        
        # If setting as default, unset others
        if data.is_default:
            for addr in user.addresses:
                addr.is_default = False
        
        address.label = data.label
        address.street = data.street
        address.city = data.city
        address.state = data.state
        address.landmark = data.landmark
        address.is_default = data.is_default
        
        self.db.commit()
        self.db.refresh(address)
        
        return AddressResponse.model_validate(address)
    
    def delete_address(self, user: User, address_id: int) -> None:
        """Delete address."""
        address = self.db.query(Address).filter(
            Address.id == address_id,
            Address.user_id == user.id,
        ).first()
        
        if not address:
            raise NotFoundException("Address", address_id)
        
        was_default = address.is_default
        
        self.db.delete(address)
        self.db.commit()
        
        # If deleted address was default, set another as default
        if was_default and user.addresses:
            self.db.refresh(user)
            if user.addresses:
                user.addresses[0].is_default = True
                self.db.commit()
    
    def set_default_address(self, user: User, address_id: int) -> AddressResponse:
        """Set address as default."""
        address = self.db.query(Address).filter(
            Address.id == address_id,
            Address.user_id == user.id,
        ).first()
        
        if not address:
            raise NotFoundException("Address", address_id)
        
        # Unset other defaults
        for addr in user.addresses:
            addr.is_default = False
        
        address.is_default = True
        self.db.commit()
        self.db.refresh(address)
        
        return AddressResponse.model_validate(address)
