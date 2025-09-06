import logging
from datetime import datetime, timezone

import redis

from app.config.settings import settings

logger = logging.getLogger(__name__)

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
        try:
            ttl = int((expires_at - datetime.now(timezone.utc)).total_seconds())
            if ttl > 0:
                self.redis_client.setex(f"blacklist:{token}", ttl, "1")
                logger.debug(f"Token added to blacklist with TTL: {ttl}")
        except Exception as e:
            logger.error(f"Failed to add token to blacklist: {e}")
    
    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        try:
            logger.debug("Checking if token is blacklisted")
            exists = self.redis_client.exists(f"blacklist:{token}")
            logger.debug(f"Token blacklisted: {exists > 0}")
            return exists > 0
        except Exception as e:
            logger.error(f"Failed to check token blacklist status: {e}")
            # Return False to allow token verification to continue if Redis is down
            return False

    async def remove_from_blacklist(self, token: str):
        """Remove token from blacklist"""
        try:
            result = await self.redis_client.delete(f"blacklist:{token}")
            logger.debug(f"Token removed from blacklist: {result}")
        except Exception as e:
            logger.error(f"Failed to remove token from blacklist: {e}")

# Global blacklist instance
token_blacklist = TokenBlacklist()