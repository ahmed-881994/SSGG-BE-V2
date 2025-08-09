from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    # #APP settings
    # environment: str
    
    # Database settings
    db_host: str
    db_port: int = 3306
    db_database: str
    db_username: str
    db_password: str


    # Database connection pool settings
    db_max_connections: int = 20
    db_min_connections: int = 5

    # Redis settings
    rds_host: str
    rds_port: int = 6379
    rds_database: int = 0
    
    # JWT settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expires_minutes: int = 30
    
    # Security settings
    cors_origins: str = "*"
    rate_limit_per_minute: int = 60
    
    # Logging settings
    log_level: str = "INFO"
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v
    
    @validator("db_password")
    def validate_password(cls, v):
        if not v:
            raise ValueError("Database password cannot be empty")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()