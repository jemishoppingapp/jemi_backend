from fastapi import HTTPException, status
from typing import Optional, Any


class JEMIException(HTTPException):
    """Base exception for JEMI API."""
    
    def __init__(
        self,
        status_code: int,
        message: str,
        code: Optional[str] = None,
        errors: Optional[dict[str, list[str]]] = None,
    ):
        detail = {"message": message}
        if code:
            detail["code"] = code
        if errors:
            detail["errors"] = errors
        
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(JEMIException):
    """Resource not found exception."""
    
    def __init__(self, resource: str = "Resource", resource_id: Any = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with ID '{resource_id}' not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            code="NOT_FOUND",
        )


class UnauthorizedException(JEMIException):
    """Unauthorized access exception."""
    
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            code="UNAUTHORIZED",
        )


class ForbiddenException(JEMIException):
    """Forbidden access exception."""
    
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            code="FORBIDDEN",
        )


class BadRequestException(JEMIException):
    """Bad request exception."""
    
    def __init__(
        self,
        message: str = "Bad request",
        errors: Optional[dict[str, list[str]]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            code="BAD_REQUEST",
            errors=errors,
        )


class ConflictException(JEMIException):
    """Conflict exception (e.g., duplicate resource)."""
    
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            code="CONFLICT",
        )


class InsufficientStockException(JEMIException):
    """Insufficient stock exception."""
    
    def __init__(self, product_name: str, available: int, requested: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Insufficient stock for '{product_name}'. Available: {available}, Requested: {requested}",
            code="INSUFFICIENT_STOCK",
        )


class PaymentFailedException(JEMIException):
    """Payment processing failed exception."""
    
    def __init__(self, message: str = "Payment processing failed"):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            message=message,
            code="PAYMENT_FAILED",
        )
