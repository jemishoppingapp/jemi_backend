from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException
from app.models.user import User

# Security scheme for JWT
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get current authenticated user.
    Raises UnauthorizedException if not authenticated or token invalid.
    """
    if not credentials:
        raise UnauthorizedException("Authentication required")
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise UnauthorizedException("Invalid or expired token")
    
    # Check token type
    if payload.get("type") != "access":
        raise UnauthorizedException("Invalid token type")
    
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user:
        raise UnauthorizedException("User not found")
    
    if not user.is_active:
        raise UnauthorizedException("User account is disabled")
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Dependency to get current user if authenticated, None otherwise.
    Does not raise exceptions for unauthenticated requests.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except UnauthorizedException:
        return None


# Type alias for cleaner route signatures
CurrentUser = User
OptionalUser = Optional[User]
