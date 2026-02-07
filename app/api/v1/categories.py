from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product import CategoryResponse
from app.schemas.common import ApiResponse
from app.services.product import ProductService

router = APIRouter()


@router.get("", response_model=ApiResponse[list[CategoryResponse]])
def get_categories(db: Session = Depends(get_db)):
    """
    Get all categories.
    
    - GET /api/v1/categories
    - Matches frontend: ENDPOINTS.CATEGORIES.BASE
    """
    service = ProductService(db)
    result = service.get_categories()
    return ApiResponse(data=result, success=True)


@router.get("/{category_id}", response_model=ApiResponse[CategoryResponse])
def get_category(category_id: str, db: Session = Depends(get_db)):
    """
    Get single category by slug/ID.
    
    - GET /api/v1/categories/{id}
    - Matches frontend: ENDPOINTS.CATEGORIES.DETAIL(id)
    """
    service = ProductService(db)
    result = service.get_category_by_slug(category_id)
    return ApiResponse(data=result, success=True)
