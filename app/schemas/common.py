from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper - matches frontend ApiResponse<T>"""
    data: T
    message: Optional[str] = None
    success: bool = True


class ApiError(BaseModel):
    """Error response - matches frontend ApiError"""
    message: str
    code: Optional[str] = None
    errors: Optional[dict[str, list[str]]] = None


class PaginationParams(BaseModel):
    """Pagination parameters - matches frontend PaginationParams"""
    page: int = 1
    limit: int = 20


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response - matches frontend PaginatedResponse<T>"""
    data: list[T]
    total: int
    page: int
    limit: int
    total_pages: int
    
    @classmethod
    def create(cls, data: list[T], total: int, page: int, limit: int):
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        return cls(
            data=data,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
