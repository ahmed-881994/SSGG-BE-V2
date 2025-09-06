"""
Token Service Module

Centralized token management service for JWT operations including
token creation, verification, and blacklisting.
"""

import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
import logging

# from app.config.logging_config import logger
from app.config.settings import settings
from app.core.exceptions import InvalidTokenError
from app.core.token_blacklist import token_blacklist

logger = logging.getLogger(__name__)

class TokenService:
    """Centralized token management service"""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expires_minutes
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token
        
        Args:
            data: Token payload data
            expires_delta: Custom expiration time
            
        Returns:
            str: Encoded JWT token
        """
        logger.debug("Creating access token")
        start_time = time.time()
        
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.now(timezone.utc) + expires_delta
            else:
                expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
            
            to_encode.update({"exp": expire, "type": "access"})
            token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            
            creation_time = round((time.time() - start_time) * 1000, 2)
            logger.debug(f"Access token created successfully in {creation_time}ms")
            return token
            
        except Exception as e:
            creation_time = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Token creation failed after {creation_time}ms: {str(e)}", exc_info=True)
            raise InvalidTokenError(message="Token creation error", name=None)
    
    def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT refresh token
        
        Args:
            data: Token payload data
            expires_delta: Custom expiration time
            
        Returns:
            str: Encoded JWT refresh token
        """
        logger.debug("Creating refresh token")
        start_time = time.time()
        
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.now(timezone.utc) + expires_delta
            else:
                expire = datetime.now(timezone.utc) + timedelta(days=7)
            
            to_encode.update({"exp": expire, "type": "refresh"})
            token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            
            creation_time = round((time.time() - start_time) * 1000, 2)
            logger.debug(f"Refresh token created successfully in {creation_time}ms")
            return token
            
        except Exception as e:
            creation_time = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Refresh token creation failed after {creation_time}ms: {str(e)}", exc_info=True)
            raise InvalidTokenError(message="Token creation error", name=None)

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token to verify
            token_type: Expected token type (access/refresh)
            
        Returns:
            Dict: Decoded token payload
            
        Raises:
            InvalidTokenError: If token is invalid, expired, or blacklisted
        """
        logger.debug(f"Verifying {token_type} token")
        # start_time = time.time()
        
        try:
            # Check if token is blacklisted
            if token_blacklist.is_blacklisted(token):
                logger.warning("Token verification failed: Token is blacklisted")
                raise InvalidTokenError(message="Token has been revoked", name=None)
            
            # Decode the JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Validate token type
            if payload.get("type") != token_type:
                logger.warning(f"Token verification failed: Invalid token type. Expected {token_type}")
                raise InvalidTokenError(message=f"Invalid token type. Expected {token_type}", name=None)
            
            # # Check expiration
            # exp = payload.get("exp")
            # if exp and datetime.now(timezone.utc).timestamp() > exp:
            #     logger.warning("Token verification failed: Token has expired")
            #     raise InvalidTokenError(message="Token has expired", name=None)
            # verification_time = round((time.time() - start_time) * 1000, 2)
            logger.debug(f"Token verification successful")
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token verification failed: Token has expired")
            raise InvalidTokenError(message="Token has expired", name='TokenService')
        except jwt.PyJWTError as e:
            # verification_time = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"Token verification failed Invalid JWT format - {str(e)}")
            raise InvalidTokenError(message="Invalid token format", name='TokenService')
        except InvalidTokenError:
            # Re-raise custom exceptions without additional logging
            raise
        except Exception as e:
            # verification_time = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Unexpected error during token verification: {str(e)}", exc_info=True)
            raise InvalidTokenError(message="Token verification error", name=None)
    
    def blacklist_token(self, token: str) -> bool:
        """
        Add token to blacklist until expiration
        
        Args:
            token: JWT token to blacklist
            
        Returns:
            bool: True if successfully blacklisted, False otherwise
        """
        logger.debug("Blacklisting token")
        start_time = time.time()
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            exp_timestamp = payload.get("exp")
            
            if not exp_timestamp:
                logger.warning("Token blacklisting failed: Token has no expiration timestamp")
                return False
            
            expires_at = datetime.fromtimestamp(exp_timestamp, timezone.utc)
            token_blacklist.add_to_blacklist(token, expires_at)
            
            blacklist_time = round((time.time() - start_time) * 1000, 2)
            logger.info(f"Token blacklisted successfully in {blacklist_time}ms - expires at {expires_at}")
            return True
            
        except jwt.PyJWTError as e:
            blacklist_time = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"Token blacklisting failed after {blacklist_time}ms: Invalid token format - {str(e)}")
            return False
        except Exception as e:
            blacklist_time = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Unexpected error during token blacklisting after {blacklist_time}ms: {str(e)}", exc_info=True)
            return False


# Global token service instance
token_service = TokenService()
