"""
User Authentication Service Module

This module provides comprehensive user authentication and authorization functionality
for the SSGG-BE-V2 application. It handles user authentication, JWT token validation,
user session management, and logout operations.

The authentication system includes:
- Username/password authentication
- JWT token generation and validation
- Token blacklisting for secure logout
- User session management
- Database user retrieval and validation

Security Features:
- Password hashing verification
- JWT token expiration checking
- Token blacklisting for revoked sessions
- User active status validation

Dependencies:
- FastAPI OAuth2PasswordBearer for token handling
- PyJWT for JWT token operations
- Custom token blacklist for session management
"""

import time
from datetime import datetime, timezone
import os
from typing import Annotated, Optional

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.config.settings import settings
from app.config.logging_config import logger
from app.exceptions.exceptions import AuthenticationFailed, InvalidTokenError
from app.schema.users.user import User
from app.util.pymysql_pool import db_pool
from app.util.password import verify_password
from app.util.database import get_connection
from app.util.token_blacklist import token_blacklist

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username and password.
    
    This function validates user credentials by checking the username exists
    and verifying the provided password against the stored hash.
    
    Args:
        username (str): The username to authenticate
        password (str): The plain text password to verify
        
    Returns:
        Optional[User]: User object if authentication successful, None otherwise
        
    Example:
        user = authenticate_user("john_doe", "secure_password123")
        if user:
            print(f"Authenticated user: {user.user_name}")
    """
    logger.info(f"Attempting authentication for user: {username}")
    start_time = time.time()
    
    try:
        user = get_user_by_id_db(username)
        if not user:
            logger.warning(f"Authentication failed: User '{username}' not found")
            return None
            
        if not verify_password(password, user.password_hash, user.salt):
            logger.warning(f"Authentication failed: Invalid password for user '{username}'")
            return None
            
        auth_time = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Authentication successful for user '{username}' in {auth_time}ms")
        return user
        
    except Exception as e:
        auth_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Authentication error for user '{username}' after {auth_time}ms: {str(e)}", exc_info=True)
        return None


def get_user_by_id_db(user_name: str) -> Optional[User]:
    """
    Retrieve a user from the database by username.
    
    This function queries the database to find a user with the specified username.
    It handles database connection management and user object creation.
    
    Args:
        user_name (str): The username to search for
        
    Returns:
        Optional[User]: User object if found, None otherwise
        
    Raises:
        Exception: Database connection or query errors (logged but not re-raised)
        
    Example:
        user = get_user_by_id_db("john_doe")
        if user:
            print(f"Found user: {user.user_name}")
    """
    logger.debug(f"Retrieving user from database: {user_name}")
    start_time = time.time()
    
    try:
        conn = db_pool.get_connection()
        if conn is None:
            logger.error("Failed to get database connection for user retrieval")
            return None
            
        
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE user_name = %s", (user_name,))
            user_data = cursor.fetchone()
        
        query_time = round((time.time() - start_time) * 1000, 2)
        
        if user_data:
            user = User(**user_data)
            logger.debug(f"User '{user_name}' retrieved successfully in {query_time}ms")
            return user
        else:
            logger.debug(f"User '{user_name}' not found in database (query took {query_time}ms)")
            return None
                
    except Exception as e:
        query_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Database error retrieving user '{user_name}' after {query_time}ms: {str(e)}", exc_info=True)
        return None
    finally:
        if conn:
            db_pool.return_connection(conn)


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Validate JWT token and return the current authenticated user.
    
    This function is used as a FastAPI dependency to protect routes that require
    authentication. It validates the JWT token, checks for blacklisting and
    expiration, and retrieves the associated user.
    
    Args:
        token (str): JWT token from the Authorization header
        
    Returns:
        User: The authenticated user object
        
    Raises:
        InvalidTokenError: If token is invalid, expired, or blacklisted
        AuthenticationFailed: If user credentials are invalid
        
    Example:
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"message": f"Hello {current_user.user_name}"}
    """
    logger.debug("Validating JWT token for current user")
    start_time = time.time()
    
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm

    try:
        # Check if token is blacklisted
        if token_blacklist.is_blacklisted(token):
            logger.warning("Token validation failed: Token is blacklisted")
            raise InvalidTokenError(message="Token has been revoked", name=None)
        
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.now(timezone.utc).timestamp() > exp:
            logger.warning("Token validation failed: Token has expired")
            raise InvalidTokenError(message="Token has expired", name=None)
        
        user_name = payload.get("sub")
        if user_name is None:
            logger.warning("Token validation failed: Missing user subject")
            raise AuthenticationFailed(message="Invalid credentials", name=None)
        
        # Retrieve user from database
        user = get_user_by_id_db(user_name)
        if not user:
            logger.warning(f"Token validation failed: User '{user_name}' not found in database")
            raise AuthenticationFailed(message="Invalid credentials", name=None)
        
        validation_time = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Token validation successful for user '{user_name}' in {validation_time}ms")
        return user
        
    except jwt.PyJWTError as e:
        validation_time = round((time.time() - start_time) * 1000, 2)
        logger.warning(f"Token validation failed after {validation_time}ms: Invalid JWT format - {str(e)}")
        raise InvalidTokenError(message="Invalid token", name=None)
    except (InvalidTokenError, AuthenticationFailed):
        # Re-raise custom exceptions without additional logging
        raise
    except Exception as e:
        validation_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Unexpected error during token validation after {validation_time}ms: {str(e)}", exc_info=True)
        raise InvalidTokenError(message="Token validation error", name=None)


async def login_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Validate user login and check active status.
    
    This function validates that a user is active and can perform authenticated
    operations. It's typically used after successful token validation.
    
    Args:
        current_user (User): The authenticated user from token validation
        
    Returns:
        User: The validated user object
        
    Raises:
        AuthenticationFailed: If the user is inactive
        
    Example:
        @app.post("/login")
        async def login(current_user: User = Depends(login_user)):
            return {"message": f"Welcome {current_user.user_name}"}
    """
    logger.debug(f"Validating login for user: {current_user.user_name}")
    
    if current_user.is_active == 0:
        logger.warning(f"Login failed: User '{current_user.user_name}' is inactive")
        raise AuthenticationFailed(message="User is not active", name=None)
    
    logger.info(f"Login validation successful for user: {current_user.user_name}")
    return current_user


def logout_user(token: str) -> bool:
    """
    Logout a user by blacklisting their JWT token.
    
    This function adds the provided JWT token to the blacklist until its
    expiration time, effectively invalidating the token for future requests.
    
    Args:
        token (str): The JWT token to blacklist
        
    Returns:
        bool: True if logout successful, False if token is invalid
        
    Example:
        success = logout_user("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")
        if success:
            print("User logged out successfully")
    """
    logger.info("Processing user logout request")
    start_time = time.time()
    
    try:
        # Decode the token to get its expiration
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp_timestamp = payload.get("exp")
        
        if not exp_timestamp:
            logger.warning("Logout failed: Token has no expiration timestamp")
            return False
            
        expires_at = datetime.fromtimestamp(exp_timestamp, timezone.utc)
        token_blacklist.add_to_blacklist(token, expires_at)
        
        logout_time = round((time.time() - start_time) * 1000, 2)
        logger.info(f"User logout successful in {logout_time}ms - token blacklisted until {expires_at}")
        return True
        
    except jwt.PyJWTError as e:
        logout_time = round((time.time() - start_time) * 1000, 2)
        logger.warning(f"Logout failed after {logout_time}ms: Invalid token format - {str(e)}")
        return False
    except Exception as e:
        logout_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Unexpected error during logout after {logout_time}ms: {str(e)}", exc_info=True)
        return False