from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional

from app.models.product import Product, Category
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductDetailResponse,
    ProductListResponse,
    ProductFilter,
    CategoryResponse,
)
from app.core.exceptions import NotFoundException
from app.utils.formatters import slugify


class ProductService:
    """Service for product operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_products(
        self,
        page: int = 1,
        limit: int = 20,
        filters: Optional[ProductFilter] = None,
    ) -> ProductListResponse:
        """Get paginated list of products with optional filters."""
        query = self.db.query(Product).filter(Product.is_active == True)
        
        if filters:
            # Category filter
            if filters.category and filters.category != "all":
                query = query.filter(Product.category == filters.category)
            
            # Search filter
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Product.name.ilike(search_term),
                        Product.description.ilike(search_term),
                    )
                )
            
            # Price range
            if filters.min_price is not None:
                query = query.filter(Product.price >= filters.min_price)
            if filters.max_price is not None:
                query = query.filter(Product.price <= filters.max_price)
            
            # Stock filter
            if filters.in_stock is not None:
                if filters.in_stock:
                    query = query.filter(
                        and_(Product.in_stock == True, Product.stock_quantity > 0)
                    )
                else:
                    query = query.filter(
                        or_(Product.in_stock == False, Product.stock_quantity <= 0)
                    )
            
            # Featured/Trending
            if filters.is_featured:
                query = query.filter(Product.is_featured == True)
            if filters.is_trending:
                query = query.filter(Product.is_trending == True)
            
            # Sorting
            sort_column = getattr(Product, filters.sort_by, Product.created_at)
            if filters.sort_order == "asc":
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(Product.created_at.desc())
        
        # Get total count
        total = query.count()
        
        # Paginate
        offset = (page - 1) * limit
        products = query.offset(offset).limit(limit).all()
        
        # Convert to response
        product_responses = [ProductResponse.from_orm_model(p) for p in products]
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        
        return ProductListResponse(
            products=product_responses,
            total=total,
            page=page,
            limit=limit,
            totalPages=total_pages,
        )
    
    def get_product_by_id(self, product_id: int) -> ProductDetailResponse:
        """Get single product by ID."""
        product = self.db.query(Product).filter(
            Product.id == product_id,
            Product.is_active == True,
        ).first()
        
        if not product:
            raise NotFoundException("Product", product_id)
        
        return ProductDetailResponse.from_orm_model(product)
    
    def get_products_by_category(
        self,
        category: str,
        page: int = 1,
        limit: int = 20,
    ) -> ProductListResponse:
        """Get products by category slug."""
        filters = ProductFilter(category=category)
        return self.get_products(page=page, limit=limit, filters=filters)
    
    def get_featured_products(self, limit: int = 8) -> list[ProductResponse]:
        """Get featured products."""
        products = self.db.query(Product).filter(
            Product.is_active == True,
            Product.is_featured == True,
        ).limit(limit).all()
        
        return [ProductResponse.from_orm_model(p) for p in products]
    
    def get_trending_products(self, limit: int = 8) -> list[ProductResponse]:
        """Get trending products."""
        products = self.db.query(Product).filter(
            Product.is_active == True,
            Product.is_trending == True,
        ).limit(limit).all()
        
        return [ProductResponse.from_orm_model(p) for p in products]
    
    def search_products(
        self,
        query: str,
        page: int = 1,
        limit: int = 20,
    ) -> ProductListResponse:
        """Search products by name or description."""
        filters = ProductFilter(search=query)
        return self.get_products(page=page, limit=limit, filters=filters)
    
    def get_categories(self) -> list[CategoryResponse]:
        """Get all active categories."""
        categories = self.db.query(Category).filter(
            Category.is_active == True
        ).order_by(Category.sort_order).all()
        
        return [CategoryResponse.from_orm_model(c) for c in categories]
    
    def get_category_by_slug(self, slug: str) -> CategoryResponse:
        """Get category by slug."""
        category = self.db.query(Category).filter(
            Category.slug == slug,
            Category.is_active == True,
        ).first()
        
        if not category:
            raise NotFoundException("Category", slug)
        
        return CategoryResponse.from_orm_model(category)
    
    def create_product(self, data: ProductCreate) -> ProductResponse:
        """Create a new product (admin only)."""
        # Generate slug if not provided
        slug = data.slug or slugify(data.name)
        
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while self.db.query(Product).filter(Product.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        product = Product(
            name=data.name,
            slug=slug,
            description=data.description,
            price=data.price,
            compare_at_price=data.compare_at_price,
            image_url=data.image_url,
            image_alt=data.image_alt,
            color=data.color,
            category=data.category,
            category_id=data.category_id,
            stock_quantity=data.stock_quantity,
            in_stock=data.stock_quantity > 0,
            is_featured=data.is_featured,
            is_trending=data.is_trending,
        )
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        
        return ProductResponse.from_orm_model(product)
