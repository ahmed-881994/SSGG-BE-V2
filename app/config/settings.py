from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # #APP settings
    environment: str
    
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

    # OpenTelemetry settings
    otel_exporter_otlp_endpoint: str = ""
    otel_service_name: str = "ssgg-api"
    otel_log_correlation: bool = True
    
    # SMTP settings
    smtp_server: str
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    from_email: str

    # @validator("secret_key")
    # def validate_secret_key(cls, v):
    #     if len(v) < 32:
    #         raise ValueError("Secret key must be at least 32 characters long")
    #     return v
    
    # @validator("db_password")
    # def validate_password(cls, v):
    #     if not v:
    #         raise ValueError("Database password cannot be empty")
    #     return v
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # This will ignore extra fields in .env
    }

# Global settings instance
settings = Settings()