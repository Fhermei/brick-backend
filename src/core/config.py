from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    APP_NAME: str = "Brick SPMES API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str
    POSTGRES_DB: str = "brickdatabase"
    POSTGRES_USER: str = "brick"
    POSTGRES_PASSWORD: str = "Fatunbi11."

    # Redis - Made optional with default None
    REDIS_URL: Optional[str] = None

    # AWS Cognito
    AWS_REGION: str
    COGNITO_CLIENT_ID: str
    COGNITO_CLIENT_SECRET: str
    COGNITO_USER_POOL_ID: str

    # SMTP Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@brickapp.com"
    SMTP_USE_TLS: bool = True

    # Frontend URL
    FRONTEND_URL: str = "http://localhost:5173"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,https://brick-frontend-beige.vercel.app"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # This ignores extra environment variables


settings = Settings()