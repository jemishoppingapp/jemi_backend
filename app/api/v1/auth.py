from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import LoginCredentials, RegisterData, AuthResponse
from app.schemas.common import ApiResponse
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=ApiResponse[AuthResponse], status_code=status.HTTP_201_CREATED)
def register(data: RegisterData, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - POST /api/v1/auth/register
    - Matches frontend: ENDPOINTS.AUTH.REGISTER
    """
    service = AuthService(db)
    result = service.register(data)
    return ApiResponse(data=result, message="Registration successful", success=True)


@router.post("/login", response_model=ApiResponse[AuthResponse])
def login(credentials: LoginCredentials, db: Session = Depends(get_db)):
    """
    Authenticate user and return tokens.
    
    - POST /api/v1/auth/login
    - Matches frontend: ENDPOINTS.AUTH.LOGIN
    """
    service = AuthService(db)
    result = service.login(credentials.email, credentials.password)
    return ApiResponse(data=result, message="Login successful", success=True)


@router.post("/refresh", response_model=ApiResponse[dict])
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    
    - POST /api/v1/auth/refresh
    - Matches frontend: ENDPOINTS.AUTH.REFRESH
    """
    service = AuthService(db)
    result = service.refresh_tokens(refresh_token)
    return ApiResponse(data=result, message="Tokens refreshed", success=True)


@router.post("/logout", response_model=ApiResponse[dict])
def logout():
    """
    Logout user (client-side token invalidation).
    
    - POST /api/v1/auth/logout
    - Matches frontend: ENDPOINTS.AUTH.LOGOUT
    
    Note: JWT tokens are stateless. Actual logout is handled client-side
    by removing the token. This endpoint is for API consistency.
    """
    return ApiResponse(data={"logged_out": True}, message="Logout successful", success=True)


@router.post("/forgot-password", response_model=ApiResponse[dict])
def forgot_password(email: str):
    """
    Request password reset email.
    
    - POST /api/v1/auth/forgot-password
    - Matches frontend: ENDPOINTS.AUTH.FORGOT_PASSWORD
    
    TODO: Implement email sending with reset link
    """
    # TODO: Implement password reset email
    return ApiResponse(
        data={"sent": True},
        message="If an account exists with this email, a reset link will be sent",
        success=True,
    )


@router.post("/reset-password", response_model=ApiResponse[dict])
def reset_password(token: str, new_password: str):
    """
    Reset password using token from email.
    
    - POST /api/v1/auth/reset-password
    - Matches frontend: ENDPOINTS.AUTH.RESET_PASSWORD
    
    TODO: Implement password reset with token validation
    """
    # TODO: Implement password reset
    return ApiResponse(
        data={"reset": True},
        message="Password reset successful",
        success=True,
    )
