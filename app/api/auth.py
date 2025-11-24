"""
Authentication API Router

Handles authentication endpoints including login, logout, and token refresh.
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pymysql import MySQLError
from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.database import get_db_session
from app.core.exceptions import AuthenticationFailed, ServiceError
from app.core.rate_limitting import rate_limit
from app.schemas.auth_schema import Token
from app.services.auth_service import AuthService, oauth2_scheme
from app.services.token_service import token_service
from app.services.user_service import UserService

router = APIRouter(tags=["Authentication"])


@router.post("/token", response_model=Token)
@rate_limit("10/minute")
def login(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db_session)):
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
    # start_time = time.time()
    
    try:
        auth_service = AuthService(db)
        user = auth_service.authenticate_user(form_data.username, form_data.password)

        if not user.is_active:
            raise AuthenticationFailed(message="User is not active", name="Authentication")
        
        user_service = UserService(db)
        
        user_permissions = user_service.get_user_permissions_by_id(user.id)

        token_data = {"sub": str(user.id), "member_id": str(user.user_id), "role": user.role.name if user.role else None, "permissions": user_permissions}
        access_token = token_service.create_access_token(
            data=token_data, 
            expires_delta=timedelta(minutes=token_service.access_token_expires_minutes)
        )
        refresh_token = token_service.create_refresh_token(
            data=token_data, 
            expires_delta=timedelta(days=7)
        )
        
        return Token(
            access_token=access_token, 
            token_type="bearer", 
            refresh_token=refresh_token
        )
    except AuthenticationFailed as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ServiceError as e:
        logger.error(f"Database error during login for user {form_data.username}: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Unexpected error during login for user {form_data.username}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected error")
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
    
    try:
        payload = token_service.verify_token(refresh_token, "refresh")
        id = payload.get("sub")

        if not id:
            logger.warning("Token refresh failed: Missing user subject in refresh token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = token_service.create_access_token(
            data=payload,
            expires_delta=timedelta(minutes=token_service.access_token_expires_minutes)
        )

        logger.info(f"Token refresh successful for user '{id}'")

        return Token(access_token=access_token, token_type="bearer", refresh_token=None)
        
    except Exception as e:
        logger.warning(f"Token refresh failed: {str(e)}")
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
    
    try:
        success = token_service.blacklist_token(token)
        
        if success:
            logger.info(f"User logout successful")
            return {"message": "Successfully logged out"}
        else:
            logger.warning(f"Logout failed: Invalid token")
            raise HTTPException(status_code=400, detail="Invalid token")
            
    except Exception as e:
        logger.error(f"Unexpected error during logout: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")