from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


# ============ Address Schemas ============

class AddressBase(BaseModel):
    label: str = Field(..., min_length=1, max_length=100)
    street: str = Field(..., min_length=1, max_length=500)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    landmark: Optional[str] = Field(None, max_length=255)
    is_default: bool = False


class AddressCreate(AddressBase):
    pass


class AddressResponse(AddressBase):
    id: int
    
    class Config:
        from_attributes = True


# ============ User Schemas ============

class UserBase(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    name: str = Field(..., min_length=2, max_length=255)
    
    @field_validator("phone")
    @classmethod
    def validate_nigerian_phone(cls, v: str) -> str:
        """Validate Nigerian phone number format"""
        # Remove spaces and dashes
        cleaned = re.sub(r"[\s\-]", "", v)
        
        # Nigerian phone patterns:
        # +234XXXXXXXXXX (14 chars)
        # 234XXXXXXXXXX (13 chars)
        # 0XXXXXXXXXX (11 chars)
        patterns = [
            r"^\+234[789]\d{9}$",  # +234 format
            r"^234[789]\d{9}$",    # 234 format
            r"^0[789]\d{9}$",      # Local format
        ]
        
        if not any(re.match(p, cleaned) for p in patterns):
            raise ValueError(
                "Invalid Nigerian phone number. Use format: +234XXXXXXXXXX, 234XXXXXXXXXX, or 0XXXXXXXXXX"
            )
        
        return cleaned


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserResponse(BaseModel):
    """Matches frontend User interface"""
    id: int
    name: str
    email: str
    phone: str
    avatar: Optional[str] = None
    created_at: datetime
    addresses: list[AddressResponse] = []
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Matches frontend ProfileUpdateData"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    avatar: Optional[str] = None
    
    @field_validator("phone")
    @classmethod
    def validate_nigerian_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cleaned = re.sub(r"[\s\-]", "", v)
        patterns = [
            r"^\+234[789]\d{9}$",
            r"^234[789]\d{9}$",
            r"^0[789]\d{9}$",
        ]
        if not any(re.match(p, cleaned) for p in patterns):
            raise ValueError("Invalid Nigerian phone number")
        return cleaned


# ============ Auth Schemas ============

class LoginCredentials(BaseModel):
    """Matches frontend LoginCredentials"""
    email: EmailStr
    password: str


class RegisterData(BaseModel):
    """Matches frontend RegisterData"""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("phone")
    @classmethod
    def validate_nigerian_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-]", "", v)
        patterns = [
            r"^\+234[789]\d{9}$",
            r"^234[789]\d{9}$",
            r"^0[789]\d{9}$",
        ]
        if not any(re.match(p, cleaned) for p in patterns):
            raise ValueError("Invalid Nigerian phone number")
        return cleaned


class AuthResponse(BaseModel):
    """Matches frontend AuthResponse"""
    user: UserResponse
    token: str
    refresh_token: str


class TokenData(BaseModel):
    """JWT token payload data"""
    user_id: int
    email: str
    exp: Optional[datetime] = None
