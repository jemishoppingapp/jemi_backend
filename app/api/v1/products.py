from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.product import (
    ProductResponse,
    ProductDetailResponse,
    ProductListResponse,
    ProductFilter,
)
from app.schemas.common import ApiResponse
from app.services.product import ProductService

router = APIRouter()


@router.get("", response_model=ApiResponse[ProductListResponse])
def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
):
    """
    Get paginated list of products with filters.
    
    - GET /api/v1/products
    - Matches frontend: ENDPOINTS.PRODUCTS.BASE
    
    Query params:
    - page: Page number (default 1)
    - limit: Items per page (default 20, max 100)
    - category: Filter by category slug
    - search: Search in name/description
    - min_price, max_price: Price range filter
    - in_stock: Filter by availability
    - sort_by: name, price, created_at
    - sort_order: asc, desc
    """
    service = ProductService(db)
    filters = ProductFilter(
        category=category,
        search=search,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    result = service.get_products(page=page, limit=limit, filters=filters)
    return ApiResponse(data=result, success=True)


@router.get("/featured", response_model=ApiResponse[list[ProductResponse]])
def get_featured_products(
    limit: int = Query(8, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Get featured products.
    
    - GET /api/v1/products/featured
    - Matches frontend: ENDPOINTS.PRODUCTS.FEATURED
    """
    service = ProductService(db)
    result = service.get_featured_products(limit=limit)
    return ApiResponse(data=result, success=True)


@router.get("/trending", response_model=ApiResponse[list[ProductResponse]])
def get_trending_products(
    limit: int = Query(8, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Get trending products.
    
    - GET /api/v1/products/trending
    - Matches frontend: ENDPOINTS.PRODUCTS.TRENDING
    """
    service = ProductService(db)
    result = service.get_trending_products(limit=limit)
    return ApiResponse(data=result, success=True)


@router.get("/search", response_model=ApiResponse[ProductListResponse])
def search_products(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Search products by name or description.
    
    - GET /api/v1/products/search?q=query
    - Matches frontend: ENDPOINTS.PRODUCTS.SEARCH
    """
    service = ProductService(db)
    result = service.search_products(query=q, page=page, limit=limit)
    return ApiResponse(data=result, success=True)


@router.get("/category/{category}", response_model=ApiResponse[ProductListResponse])
def get_products_by_category(
    category: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get products by category slug.
    
    - GET /api/v1/products/category/{category}
    - Matches frontend: ENDPOINTS.PRODUCTS.BY_CATEGORY(category)
    """
    service = ProductService(db)
    result = service.get_products_by_category(category=category, page=page, limit=limit)
    return ApiResponse(data=result, success=True)


@router.get("/{product_id}", response_model=ApiResponse[ProductDetailResponse])
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get single product by ID.
    
    - GET /api/v1/products/{id}
    - Matches frontend: ENDPOINTS.PRODUCTS.DETAIL(id)
    """
    service = ProductService(db)
    result = service.get_product_by_id(product_id)
    return ApiResponse(data=result, success=True)


@router.get("/{product_id}/reviews", response_model=ApiResponse[list])
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    """
    Get product reviews.
    
    - GET /api/v1/products/{id}/reviews
    - Matches frontend: ENDPOINTS.PRODUCTS.REVIEWS(id)
    
    TODO: Implement reviews feature
    """
    # TODO: Implement reviews
    return ApiResponse(data=[], message="Reviews coming soon", success=True)
