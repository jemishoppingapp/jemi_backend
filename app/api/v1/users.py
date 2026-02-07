from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, AddressCreate, AddressResponse
from app.schemas.common import ApiResponse
from app.services.user import UserService

router = APIRouter()


# ============ Profile Endpoints ============

@router.get("/profile", response_model=ApiResponse[UserResponse])
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current user's profile.
    
    - GET /api/v1/user/profile
    - Matches frontend: ENDPOINTS.USER.PROFILE
    """
    service = UserService(db)
    result = service.get_profile(current_user)
    return ApiResponse(data=result, success=True)


@router.put("/profile", response_model=ApiResponse[UserResponse])
def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's profile.
    
    - PUT /api/v1/user/profile
    - Matches frontend: ENDPOINTS.USER.PROFILE
    """
    service = UserService(db)
    result = service.update_profile(current_user, data)
    return ApiResponse(data=result, message="Profile updated", success=True)


# ============ Address Endpoints ============

@router.get("/addresses", response_model=ApiResponse[list[AddressResponse]])
def get_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user's addresses.
    
    - GET /api/v1/user/addresses
    - Matches frontend: ENDPOINTS.USER.ADDRESSES
    """
    service = UserService(db)
    result = service.get_addresses(current_user)
    return ApiResponse(data=result, success=True)


@router.post("/addresses", response_model=ApiResponse[AddressResponse], status_code=status.HTTP_201_CREATED)
def add_address(
    data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add new address.
    
    - POST /api/v1/user/addresses
    - Matches frontend: ENDPOINTS.USER.ADDRESSES
    """
    service = UserService(db)
    result = service.add_address(current_user, data)
    return ApiResponse(data=result, message="Address added", success=True)


@router.put("/addresses/{address_id}", response_model=ApiResponse[AddressResponse])
def update_address(
    address_id: int,
    data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update existing address.
    
    - PUT /api/v1/user/addresses/{id}
    - Matches frontend: ENDPOINTS.USER.ADDRESS(id)
    """
    service = UserService(db)
    result = service.update_address(current_user, address_id, data)
    return ApiResponse(data=result, message="Address updated", success=True)


@router.delete("/addresses/{address_id}", response_model=ApiResponse[dict])
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete address.
    
    - DELETE /api/v1/user/addresses/{id}
    - Matches frontend: ENDPOINTS.USER.ADDRESS(id)
    """
    service = UserService(db)
    service.delete_address(current_user, address_id)
    return ApiResponse(data={"deleted": True}, message="Address deleted", success=True)


@router.post("/addresses/{address_id}/default", response_model=ApiResponse[AddressResponse])
def set_default_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Set address as default.
    
    - POST /api/v1/user/addresses/{id}/default
    """
    service = UserService(db)
    result = service.set_default_address(current_user, address_id)
    return ApiResponse(data=result, message="Default address updated", success=True)
