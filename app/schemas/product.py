from pydantic import BaseModel, Field, computed_field
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ============ Category Schemas ============

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = Field(None, alias="imageSrc")


class CategoryCreate(CategoryBase):
    sort_order: int = 0


class CategoryResponse(BaseModel):
    """Matches frontend Category interface"""
    id: str  # Frontend uses string ID (slug)
    name: str
    href: str
    description: Optional[str] = None
    imageSrc: Optional[str] = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_model(cls, category) -> "CategoryResponse":
        return cls(
            id=category.slug,
            name=category.name,
            href=f"/products?category={category.slug}",
            description=category.description,
            imageSrc=category.image_url,
        )


# ============ Product Schemas ============

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    image_url: str
    image_alt: Optional[str] = None
    color: Optional[str] = None
    category: str
    in_stock: bool = True


class ProductCreate(ProductBase):
    slug: Optional[str] = None  # Auto-generated if not provided
    compare_at_price: Optional[Decimal] = None
    stock_quantity: int = 0
    is_featured: bool = False
    is_trending: bool = False
    category_id: int


class ProductResponse(BaseModel):
    """Matches frontend Product interface exactly"""
    id: int
    name: str
    href: str
    price: str  # Formatted with ₦ symbol
    priceValue: float  # Numeric value for calculations
    imageSrc: str
    imageAlt: str
    color: Optional[str] = None
    category: str
    inStock: bool
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_model(cls, product) -> "ProductResponse":
        """Convert SQLAlchemy model to response schema"""
        price_value = float(product.price)
        return cls(
            id=product.id,
            name=product.name,
            href=f"/products/{product.id}",
            price=f"₦{price_value:,.0f}",
            priceValue=price_value,
            imageSrc=product.image_url,
            imageAlt=product.image_alt or product.name,
            color=product.color,
            category=product.category,
            inStock=product.in_stock and product.stock_quantity > 0,
        )


class ProductDetailResponse(ProductResponse):
    """Extended product response with additional details"""
    description: Optional[str] = None
    stockQuantity: int
    sellerName: str
    isFeatured: bool
    isTrending: bool
    
    @classmethod
    def from_orm_model(cls, product) -> "ProductDetailResponse":
        price_value = float(product.price)
        return cls(
            id=product.id,
            name=product.name,
            href=f"/products/{product.id}",
            price=f"₦{price_value:,.0f}",
            priceValue=price_value,
            imageSrc=product.image_url,
            imageAlt=product.image_alt or product.name,
            color=product.color,
            category=product.category,
            inStock=product.in_stock and product.stock_quantity > 0,
            description=product.description,
            stockQuantity=product.stock_quantity,
            sellerName=product.seller_name,
            isFeatured=product.is_featured,
            isTrending=product.is_trending,
        )


class ProductListResponse(BaseModel):
    """Paginated product list"""
    products: list[ProductResponse]
    total: int
    page: int
    limit: int
    totalPages: int


class ProductFilter(BaseModel):
    """Query parameters for filtering products"""
    category: Optional[str] = None
    search: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    in_stock: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_trending: Optional[bool] = None
    sort_by: Optional[str] = "created_at"  # name, price, created_at
    sort_order: Optional[str] = "desc"  # asc, desc
