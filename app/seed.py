"""
Seed script to populate initial data.
Run with: python -m app.seed
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.product import Category, Product
from app.models.user import User
from app.core.security import hash_password


def seed_categories(db: Session):
    """Seed categories matching frontend MOCK_CATEGORIES."""
    categories = [
        {
            "slug": "fashion",
            "name": "Fashion",
            "description": "Clothes, shoes & more",
            "image_url": "https://tailwindcss.com/plus-assets/img/ecommerce-images/product-page-01-related-product-01.jpg",
            "sort_order": 1,
        },
        {
            "slug": "electronics",
            "name": "Electronics",
            "description": "Gadgets & accessories",
            "image_url": "https://tailwindcss.com/plus-assets/img/ecommerce-images/category-page-04-image-card-04.jpg",
            "sort_order": 2,
        },
        {
            "slug": "food",
            "name": "Food & Drinks",
            "description": "Snacks, drinks & groceries",
            "image_url": "https://tailwindcss.com/plus-assets/img/ecommerce-images/product-page-04-detail-product-shot-01.jpg",
            "sort_order": 3,
        },
        {
            "slug": "accessories",
            "name": "Accessories",
            "description": "Bags, wallets & more",
            "image_url": "https://tailwindcss.com/plus-assets/img/ecommerce-images/shopping-cart-page-04-product-03.jpg",
            "sort_order": 4,
        },
    ]
    
    for cat_data in categories:
        existing = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
        if not existing:
            category = Category(**cat_data)
            db.add(category)
            print(f"  Created category: {cat_data['name']}")
        else:
            print(f"  Category exists: {cat_data['name']}")
    
    db.commit()


def seed_products(db: Session):
    """Seed products matching frontend MOCK_PRODUCTS."""
    # Get category IDs
    categories = {cat.slug: cat.id for cat in db.query(Category).all()}
    
    products = [
        # Fashion
        {"name": "Basic Tee", "slug": "basic-tee-black", "price": 12500, "image_url": "https://tailwindcss.com/plus-assets/img/ecommerce-images/product-page-01-related-product-01.jpg", "image_alt": "Basic Tee in black", "color": "Black", "category": "fashion", "stock_quantity": 50, "is_featured": True},
        {"name": "Basic Tee", "slug": "basic-tee-white", "price": 12500, "image_url": "https://tailwindcss.com/plus-assets/img/ecommerce-images/product-page-01-related-product-02.jpg", "image_alt": "Basic Tee in white", "color": "White", "category": "fashion", "stock_quantity": 45},
        {"name": "Polo Shirt", "slug": "polo-shirt-gray", "price": 18000, "image_url": "https://tailwindcss.com/plus-assets/img/ecommerce-images/product-page-01-related-product-03.jpg", "image_alt": "Polo shirt", "color": "Gray", "category": "fashion", "stock_quantity": 30, "is_trending": True},
        
        # Electronics
        {"name": "Wireless Earbuds", "slug": "wireless-earbuds", "price": 25000, "image_url": "https://tailwindcss.com/plus-assets/img/ecommerce-images/category-page-04-image-card-04.jpg", "image_alt": "Wireless earbuds", "color": "White", "category": "electronics", "stock_quantity": 25, "is_featured": True, "is_trending": True},
        {"name": "Phone Charger", "slug": "phone-charger", "price": 8500, "image_url": "https://tailwindcss.com/plus-assets/img/ecommerce-images/category-page-04-image-card-02.jpg", "image_alt": "Phone charger", "color": "Black", "category": "electronics", "stock_quantity": 100},
        {"name": "USB Cable", "slug": "usb-cable", "price": 3500, "image_url": "https://tailwindcss.com/plus-assets/img/ecommerce-images/category-page-04-image-card-03.jpg", "image_alt": "USB cable", "color": "White", "category": "electronics", "stock_quantity": 150},
        
        # Food
        {"name": "Snack Pack", "slug": "snack-pack", "price": 2500, "image_url": "https://tailwindcss.com/plus-assets/img/ecommerce-images/product-page-04-detail-product-shot-01.jpg", "image_alt": "Snack pack", "color": "", "category": "food", "stock_quantity": 200},
        {"name": "Energy Drink Pack", "slug": "energy-drink-pack", "price": 4000, "image_url": "https://tailwindcss.com/plus-assets/img/ecommerce-images/category-page-04-image-card-01.jpg", "image_alt": "Energy drinks", "color": "", "category": "food", "stock_quantity": 80, "is_trending": True},
        
        # Accessories
        {"name": "Zip Tote Basket", "slug": "zip-tote-basket", "price": 50000, "image_url": "https://tailwindcss.com/plus-assets/img/ecommerce-images/shopping-cart-page-04-product-03.jpg", "image_alt": "Tote bag", "color": "White", "category": "accessories", "stock_quantity": 15, "is_featured": True},
        {"name": "Leather Wallet", "slug": "leather-wallet", "price": 15000, "image_url": "https://tailwindcss.com/plus-assets/img/ecommerce-images/shopping-cart-page-04-product-01.jpg", "image_alt": "Leather wallet", "color": "Brown", "category": "accessories", "stock_quantity": 40},
        {"name": "Backpack", "slug": "backpack-black", "price": 35000, "image_url": "https://tailwindcss.com/plus-assets/img/ecommerce-images/shopping-cart-page-04-product-02.jpg", "image_alt": "Backpack", "color": "Black", "category": "accessories", "stock_quantity": 20, "is_featured": True, "is_trending": True},
    ]
    
    for prod_data in products:
        existing = db.query(Product).filter(Product.slug == prod_data["slug"]).first()
        if not existing:
            category_slug = prod_data.pop("category")
            product = Product(
                **prod_data,
                category=category_slug,
                category_id=categories.get(category_slug, 1),
                in_stock=prod_data.get("stock_quantity", 0) > 0,
            )
            db.add(product)
            print(f"  Created product: {prod_data['name']} ({prod_data['slug']})")
        else:
            print(f"  Product exists: {prod_data['name']}")
    
    db.commit()


def seed_test_user(db: Session):
    """Create a test user for development."""
    existing = db.query(User).filter(User.email == "test@jemi.ng").first()
    if not existing:
        user = User(
            email="test@jemi.ng",
            phone="+2348012345678",
            name="Test User",
            hashed_password=hash_password("password123"),
            is_verified=True,
        )
        db.add(user)
        db.commit()
        print("  Created test user: test@jemi.ng / password123")
    else:
        print("  Test user exists: test@jemi.ng")


def run_seed():
    """Run all seed functions."""
    print("\n🌱 Seeding JEMI database...\n")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("📁 Seeding categories...")
        seed_categories(db)
        
        print("\n📦 Seeding products...")
        seed_products(db)
        
        print("\n👤 Seeding test user...")
        seed_test_user(db)
        
        print("\n✅ Seeding complete!\n")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
