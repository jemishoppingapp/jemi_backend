from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.api.v1.router import router as v1_router
from app.core.exceptions import JEMIException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Create tables (for development)
    # In production, use Alembic migrations
    if settings.DEBUG:
        Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: cleanup if needed


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    JEMI - University Student Ecommerce Marketplace API
    
    A platform for university students to buy and sell products with on-campus pickup.
    
    ## Features
    - User authentication with Nigerian phone validation
    - Product catalog with categories
    - Shopping cart
    - Order management with pickup codes
    - Wishlist
    
    ## Authentication
    Most endpoints require JWT authentication. Include the token in the Authorization header:
    ```
    Authorization: Bearer <your_token>
    ```
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(JEMIException)
async def jemi_exception_handler(request: Request, exc: JEMIException):
    """Handle custom JEMI exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail.get("message", "An error occurred"),
            "code": exc.detail.get("code"),
            "errors": exc.detail.get("errors"),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    if settings.DEBUG:
        # Show detailed error in development
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(exc),
                "code": "INTERNAL_ERROR",
            },
        )
    else:
        # Hide details in production
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "An unexpected error occurred",
                "code": "INTERNAL_ERROR",
            },
        )


# Include API routes
app.include_router(v1_router, prefix=settings.API_V1_PREFIX)


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """Root endpoint with API info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs" if settings.DEBUG else None,
        "health": "/health",
    }
