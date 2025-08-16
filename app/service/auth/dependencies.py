"""
Authentication Dependencies Module

FastAPI dependencies for authentication and authorization.
"""

import time
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.config.logging_config import logger
from app.core.exceptions import AuthenticationFailed, InvalidTokenError
from app.schema.users.user import User
from app.service.auth.auth_service import auth_service
from app.service.auth.token_service import token_service

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User: The authenticated user object
        
    Raises:
        InvalidTokenError: If token is invalid, expired, or blacklisted
        AuthenticationFailed: If user credentials are invalid
    """
    logger.debug("Validating JWT token for current user")
    start_time = time.time()
    
    try:
        # Verify token
        payload = token_service.verify_token(token, "access")
        
        # Extract username
        username = payload.get("sub")
        if not username:
            logger.warning("Token validation failed: Missing user subject")
            raise AuthenticationFailed(message="Invalid credentials", name=None)
        
        # Get user from database
        user = auth_service.get_user_by_username(username)
        if not user:
            logger.warning(f"Token validation failed: User '{username}' not found in database")
            raise AuthenticationFailed(message="Invalid credentials", name=None)
        
        validation_time = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Token validation successful for user '{username}' in {validation_time}ms")
        return user
        
    except (InvalidTokenError, AuthenticationFailed):
        # Re-raise custom exceptions without additional logging
        raise
    except Exception as e:
        validation_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Unexpected error during token validation after {validation_time}ms: {str(e)}", exc_info=True)
        raise InvalidTokenError(message="Token validation error", name=None)


def get_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    Get current user and validate they are active
    
    Args:
        current_user: The authenticated user from token validation
        
    Returns:
        User: The validated active user object
        
    Raises:
        AuthenticationFailed: If the user is inactive
    """
    logger.debug(f"Validating user is active: {current_user.user_name}")
    auth_service.validate_user_active(current_user)
    logger.info(f"User validation successful for: {current_user.user_name}")
    return current_user
