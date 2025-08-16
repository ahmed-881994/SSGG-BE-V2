"""
Authentication API Router

Handles authentication endpoints including login, logout, and token refresh.
"""

import time
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pymysql import MySQLError

from app.config.logging_config import logger
from app.exceptions.exceptions import AuthenticationFailed, ServiceError
from app.middleware.rate_limitting import rate_limit
from app.schema.auth.Token import Token
from app.service.auth.auth_service import auth_service
from app.service.auth.dependencies import oauth2_scheme
from app.service.auth.token_service import token_service

router = APIRouter(tags=["Authentication"])


@router.post("/token", response_model=Token)
@rate_limit("10/minute")
def login(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Authenticate user and return access and refresh tokens
    
    Args:
        request: FastAPI request object (for rate limiting)
        form_data: OAuth2 form data containing username and password
        
    Returns:
        Token: Object containing access_token, token_type, and refresh_token
        
    Raises:
        HTTPException: If authentication fails or user is inactive
        ServiceError: If database error occurs
    """
    logger.info(f"Login attempt for user: {form_data.username}")
    start_time = time.time()
    
    try:
        # Authenticate user
        user = auth_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            login_time = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"Login failed for user '{form_data.username}' after {login_time}ms")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validate user is active
        auth_service.validate_user_active(user)
        
        # Create tokens
        token_data = {"sub": user.user_name, "user_type": user.user_type}
        access_token = token_service.create_access_token(
            data=token_data, 
            expires_delta=timedelta(minutes=token_service.access_token_expire_minutes)
        )
        refresh_token = token_service.create_refresh_token(
            data=token_data, 
            expires_delta=timedelta(days=7)
        )
        
        login_time = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Login successful for user '{user.user_name}' in {login_time}ms")
        
        return Token(
            access_token=access_token, 
            token_type="bearer", 
            refresh_token=refresh_token
        )
        
    except AuthenticationFailed as e:
        login_time = round((time.time() - start_time) * 1000, 2)
        logger.warning(f"Login failed for user '{form_data.username}' after {login_time}ms: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except MySQLError as error:
        login_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Database error during login for user '{form_data.username}' after {login_time}ms: {error.args}")
        raise ServiceError(message=error.args[1], name="Database Error")
    except Exception as e:
        login_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Unexpected error during login for user '{form_data.username}' after {login_time}ms: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/refresh", response_model=Token)
@rate_limit("5/minute")
def refresh_access_token(request: Request, refresh_token: str):
    """
    Refresh access token using refresh token
    
    Args:
        request: FastAPI request object (for rate limiting)
        refresh_token: Valid refresh token
        
    Returns:
        Token: Object containing new access_token and token_type
        
    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    logger.info("Access token refresh requested")
    start_time = time.time()
    
    try:
        payload = token_service.verify_token(refresh_token, "refresh")
        username = payload.get("sub")
        user_type = payload.get("user_type")
        
        if not username:
            logger.warning("Token refresh failed: Missing user subject in refresh token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new access token
        access_token = token_service.create_access_token(
            data={"sub": username, "user_type": user_type}
        )
        
        refresh_time = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Token refresh successful for user '{username}' in {refresh_time}ms")
        
        return Token(access_token=access_token, token_type="bearer", refresh_token=None)
        
    except Exception as e:
        refresh_time = round((time.time() - start_time) * 1000, 2)
        logger.warning(f"Token refresh failed after {refresh_time}ms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout")
@rate_limit("10/minute")
def logout(request: Request, token: str = Depends(oauth2_scheme)):
    """
    Logout user by blacklisting their access token
    
    Args:
        request: FastAPI request object (for rate limiting)
        token: Current access token to blacklist
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If token is invalid
    """
    logger.info("User logout requested")
    start_time = time.time()
    
    try:
        success = token_service.blacklist_token(token)
        logout_time = round((time.time() - start_time) * 1000, 2)
        
        if success:
            logger.info(f"User logout successful in {logout_time}ms")
            return {"message": "Successfully logged out"}
        else:
            logger.warning(f"Logout failed after {logout_time}ms: Invalid token")
            raise HTTPException(status_code=400, detail="Invalid token")
            
    except Exception as e:
        logout_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Unexpected error during logout after {logout_time}ms: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")