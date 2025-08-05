from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config.settings import settings

limiter = Limiter(key_func=get_remote_address)

def setup_rate_limiting(app):
    """Setup rate limiting for the application"""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def rate_limit(limit: str = "60/minute"):
    """Decorator for rate limiting endpoints"""
    return limiter.limit(limit)