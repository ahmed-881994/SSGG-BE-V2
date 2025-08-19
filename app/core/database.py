import logging
from typing import Generator

from sqlalchemy import QueuePool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Construct database URL for SQLAlchemy
# Format: mysql+pymysql://user:password@host:port/database?charset=utf8mb4
DATABASE_URL = f"mysql+pymysql://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_database}?charset=utf8mb4"

# Create SQLAlchemy engine with optimized configuration
engine = create_engine(
    DATABASE_URL,
    # Use QueuePool for connection pooling (similar to existing pool behavior)
    poolclass=QueuePool,
    
    # Pool configuration - matching existing connection pool settings
    pool_size=settings.db_max_connections,  # Maximum number of persistent connections
    max_overflow=0,                         # No overflow connections (strict limit)
    pool_pre_ping=True,                     # Validate connections before use
    pool_recycle=3600,                      # Recycle connections every hour
    
    # Debug configuration
    echo=settings.log_level == settings.log_level,     # Log SQL queries in debug mode
    echo=settings.log_level == "DEBUG",     # Log SQL queries in debug mode
    echo_pool=settings.log_level == "DEBUG", # Log pool events in debug mode
    
    # Connection arguments passed to PyMySQL
    connect_args={
        "charset": "utf8mb4",
        "use_unicode": True,
        "autocommit": False,
        "connect_timeout": 10,
        "read_timeout": 30,
        "write_timeout": 30,
    }
)

# Create session factory
# Sessions are thread-local and should be created per request
SessionLocal = sessionmaker(
    autocommit=False,      # Manual transaction control
    autoflush=False,       # Manual flush control
    bind=engine,           # Bind to our engine
    expire_on_commit=False # Keep objects accessible after commit
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    
    This function provides a database session for each request.
    It ensures proper session lifecycle management:
    1. Creates a new session
    2. Yields it to the endpoint
    3. Handles exceptions with rollback
    4. Always closes the session
    
    Usage in FastAPI endpoints:
        @router.get("/")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session here
    """
    # Create new database session
    db = SessionLocal()
    try:
        # Yield session to the endpoint
        yield db
    except Exception as e:
        # Log error and rollback transaction on exception
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        # Always close the session to return connection to pool
        db.close()