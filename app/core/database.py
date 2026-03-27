from typing import AsyncGenerator, Generator

from prometheus_client import Counter, Gauge
from sqlalchemy import QueuePool, create_engine, event
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import Session, sessionmaker

from app.config.logging_config import logger
from app.config.settings import settings

# Construct database URL for SQLAlchemy
# Synchronous URL: mysql+pymysql://user:password@host:port/database?charset=utf8mb4
DATABASE_URL = f"mysql+pymysql://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_database}?charset=utf8mb4"

# Asynchronous URL: mysql+aiomysql://user:password@host:port/database?charset=utf8mb4
ASYNC_DATABASE_URL = f"mysql+aiomysql://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_database}?charset=utf8mb4"

# Prometheus metrics for DB pool behavior
db_pool_configured_size_gauge = Gauge(
    "ssgg_db_pool_configured_size",
    "Configured SQLAlchemy pool size per worker process"
)
db_pool_checked_out_gauge = Gauge(
    "ssgg_db_pool_checked_out_connections",
    "Currently checked out SQLAlchemy DB connections per worker process"
)
db_pool_checkout_timeouts_counter = Counter(
    "ssgg_db_pool_checkout_timeouts_total",
    "Total SQLAlchemy DB connection checkout timeout exceptions"
)

# Create SQLAlchemy engine with optimized configuration
engine = create_engine(
    DATABASE_URL,
    # Use QueuePool for connection pooling (similar to existing pool behavior)
    poolclass=QueuePool,
    
    # Pool configuration - matching existing connection pool settings
    pool_size=settings.db_pool_size,  # Maximum number of persistent connections
    max_overflow=settings.db_pool_max_overflow,  # Maximum number of overflow connections
    pool_timeout=settings.db_pool_timeout_seconds,  # Timeout for acquiring connections
    pool_recycle=settings.db_pool_recycle_seconds,  # Recycle connections after this many seconds
    pool_pre_ping=True,  # Enable pre-ping to check connection health before using it
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

def _refresh_pool_metrics() -> None:
    try:
        db_pool_configured_size_gauge.set(engine.pool.size())
        db_pool_checked_out_gauge.set(engine.pool.checkedout())
    except Exception:
        # Metrics must never break request flow
        pass


@event.listens_for(engine, "connect")
def _on_connect(dbapi_connection, connection_record):
    _refresh_pool_metrics()


@event.listens_for(engine, "checkout")
def _on_checkout(dbapi_connection, connection_record, connection_proxy):
    _refresh_pool_metrics()


@event.listens_for(engine, "checkin")
def _on_checkin(dbapi_connection, connection_record):
    _refresh_pool_metrics()


# Initialize gauges on startup
_refresh_pool_metrics()

# Create asynchronous SQLAlchemy engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    # Pool configuration
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_pool_max_overflow,
    pool_timeout=settings.db_pool_timeout_seconds,
    pool_recycle=settings.db_pool_recycle_seconds,
    pool_pre_ping=True,
  
    # Connection arguments passed to aiomysql
    connect_args={
        "charset": "utf8mb4",
        "use_unicode": True,
        "autocommit": False,
        "connect_timeout": 10,
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

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


def get_db_session() -> Generator[Session, None, None]:
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
        def endpoint(db: Session = Depends(get_db_session)):
            # Use db session here
    """
    # Create new database session
    db = SessionLocal()
    try:
        # Yield session to the endpoint
        yield db
    except Exception as e:
        # Log error and rollback transaction on exception
        logger.error(f"Database session error - ", exc_info=True)
        db.rollback()
        raise
    finally:
        # Always close the session to return connection to pool
        db.close()
        
async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an asynchronous database session for use in async contexts.
    
    Usage:
        async with get_async_db_session() as session:
            # Use session here
    """
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error(f"Async database session error - ", exc_info=True)
        await session.rollback()
        raise
    finally:
        await session.close()