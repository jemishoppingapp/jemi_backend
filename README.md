# JEMI Backend

FastAPI backend for JEMI - University Student Ecommerce Marketplace.

## Tech Stack

- **Framework**: FastAPI (Python 3.12+)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Validation**: Pydantic v2

## Project Structure

```
jemi-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry
│   ├── config.py            # Settings & environment
│   ├── database.py          # Database connection
│   ├── seed.py              # Seed data script
│   │
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py          # User, Address
│   │   ├── product.py       # Product, Category
│   │   ├── cart.py          # Cart, CartItem
│   │   ├── order.py         # Order, OrderItem, Timeline
│   │   └── wishlist.py      # WishlistItem
│   │
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── common.py        # ApiResponse, Pagination
│   │   ├── user.py          # Auth, User, Address schemas
│   │   ├── product.py       # Product, Category schemas
│   │   ├── cart.py          # Cart schemas
│   │   ├── order.py         # Order schemas
│   │   └── wishlist.py      # Wishlist schemas
│   │
│   ├── api/                 # API routes
│   │   ├── deps.py          # Dependencies (auth, db)
│   │   └── v1/
│   │       ├── router.py    # Main v1 router
│   │       ├── auth.py      # /auth/* endpoints
│   │       ├── products.py  # /products/* endpoints
│   │       ├── categories.py
│   │       ├── cart.py
│   │       ├── orders.py
│   │       ├── users.py
│   │       └── wishlist.py
│   │
│   ├── services/            # Business logic layer
│   │   ├── auth.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   └── user.py
│   │
│   ├── core/                # Core utilities
│   │   ├── security.py      # JWT, password hashing
│   │   ├── validators.py    # Nigerian phone validation
│   │   └── exceptions.py    # Custom HTTP exceptions
│   │
│   └── utils/
│       └── formatters.py    # Naira formatting, dates
│
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Start PostgreSQL and API
docker-compose up -d

# Seed database
docker-compose exec api python -m app.seed

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 4. Start PostgreSQL (ensure it's running)

# 5. Run migrations / create tables
python -c "from app.database import Base, engine; Base.metadata.create_all(engine)"

# 6. Seed initial data
python -m app.seed

# 7. Start server
uvicorn app.main:app --reload

# API available at http://localhost:8000
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login & get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products` | List products (paginated, filterable) |
| GET | `/api/v1/products/{id}` | Get product details |
| GET | `/api/v1/products/featured` | Featured products |
| GET | `/api/v1/products/trending` | Trending products |
| GET | `/api/v1/products/category/{slug}` | Products by category |
| GET | `/api/v1/products/search?q=query` | Search products |

### Categories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/categories` | List all categories |
| GET | `/api/v1/categories/{slug}` | Get category |

### Cart (Auth Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/cart` | Get cart |
| POST | `/api/v1/cart/items` | Add item to cart |
| PUT | `/api/v1/cart/items/{id}` | Update item quantity |
| DELETE | `/api/v1/cart/items/{id}` | Remove item |
| DELETE | `/api/v1/cart/clear` | Clear cart |

### Orders (Auth Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/orders` | List user orders |
| POST | `/api/v1/orders` | Create order from cart |
| GET | `/api/v1/orders/{id}` | Get order details |
| POST | `/api/v1/orders/{id}/cancel` | Cancel order |
| GET | `/api/v1/orders/{id}/track` | Track order |

### User Profile (Auth Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/user/profile` | Get profile |
| PUT | `/api/v1/user/profile` | Update profile |
| GET | `/api/v1/user/addresses` | List addresses |
| POST | `/api/v1/user/addresses` | Add address |
| PUT | `/api/v1/user/addresses/{id}` | Update address |
| DELETE | `/api/v1/user/addresses/{id}` | Delete address |

### Wishlist (Auth Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/wishlist` | Get wishlist |
| POST | `/api/v1/wishlist` | Add to wishlist |
| DELETE | `/api/v1/wishlist/items/{id}` | Remove from wishlist |

## Authentication

Include JWT token in Authorization header:

```
Authorization: Bearer <your_access_token>
```

## Response Format

All responses follow this structure:

```json
{
  "data": { ... },
  "message": "Optional message",
  "success": true
}
```

Error responses:

```json
{
  "success": false,
  "message": "Error description",
  "code": "ERROR_CODE",
  "errors": { "field": ["error1", "error2"] }
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT signing key | Required |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | 7 |
| `DEBUG` | Enable debug mode | false |
| `ALLOWED_ORIGINS` | CORS origins (comma-separated) | localhost |

## Frontend Integration

This backend is designed to work with the JEMI React frontend. The API endpoints match the frontend's `ENDPOINTS` configuration in `services/api/endpoints.ts`.

## Test Credentials

After seeding:
- **Email**: test@jemi.ng
- **Password**: password123

## Development

```bash
# Run tests
pytest

# Format code
black app/
isort app/

# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head
```

## License

MIT
