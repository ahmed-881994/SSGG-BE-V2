import redis
import json
from datetime import datetime, timezone
from app.config.settings import settings

class TokenBlacklist:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.rds_host,
            port=settings.rds_port,
            db=settings.rds_database,
            decode_responses=True
        )
    
    def add_to_blacklist(self, token: str, expires_at: datetime):
        """Add token to blacklist"""
        ttl = int((expires_at - datetime.now(timezone.utc)).total_seconds())
        if ttl > 0:
            self.redis_client.setex(f"blacklist:{token}", ttl, "1")
    
    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        return self.redis_client.exists(f"blacklist:{token}") > 0
    
    def remove_from_blacklist(self, token: str):
        """Remove token from blacklist"""
        self.redis_client.delete(f"blacklist:{token}")

# Global blacklist instance
token_blacklist = TokenBlacklist()