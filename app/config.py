from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "JEMI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://jemi_user:jemi_password@localhost:5432/jemi_db"
    
    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000,https://jemi.ng"
    
    # Paystack
    PAYSTACK_SECRET_KEY: str = "sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    PAYSTACK_PUBLIC_KEY: str = "pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    
    # Frontend URL (for Paystack callback)
    FRONTEND_URL: str = "http://localhost:5173"
    
    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()