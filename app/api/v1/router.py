from fastapi import APIRouter

from app.api.v1 import auth, products, categories, cart, orders, users, wishlist, payment

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(products.router, prefix="/products", tags=["Products"])
router.include_router(categories.router, prefix="/categories", tags=["Categories"])
router.include_router(cart.router, prefix="/cart", tags=["Cart"])
router.include_router(orders.router, prefix="/orders", tags=["Orders"])
router.include_router(users.router, prefix="/user", tags=["User"])
router.include_router(wishlist.router, prefix="/wishlist", tags=["Wishlist"])
router.include_router(payment.router, prefix="/payment", tags=["Payment"])