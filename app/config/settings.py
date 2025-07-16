from pydantic import BaseSettings, validator
from typing import Optional
import os

class Settings(BaseSettings):
    # Database settings
    host: str
    port: int = 3306
    database: str
    username: str
    password: str
    
    # JWT settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expires_minutes: int = 30
    
    # Security settings
    cors_origins: list = ["*"]
    rate_limit_per_minute: int = 60
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v
    
    @validator("password")
    def validate_password(cls, v):
        if not v:
            raise ValueError("Database password cannot be empty")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()