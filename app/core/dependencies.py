"""
Authentication Dependencies Module

FastAPI dependencies for authentication and authorization.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.database import get_db
from app.core.exceptions import AuthenticationFailed, ServiceError
from app.models.user import User
from app.services.token_service import token_service
from app.services.user_service import UserService

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user_in_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Get user from token and validate 

    Args:
        token: The access token

    Returns:
        User: The authenticated user

    Raises:
        HTTPException: If token is invalid or user is not found
    """
    try:
        payload = token_service.verify_token(token)
        id = payload.get("sub")
        if id is None:
            raise AuthenticationFailed(
                    message="Invalid token",
                    name="Authentication"
                )
        user_service = UserService(db)
        user = user_service.get_user_by_id(int(id))
        if user is None:
            logger.warning(f"Authentication failed: User {id} not found")
            raise AuthenticationFailed(
                message="User not found",
                name="Authentication"
            )
        return user
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        raise ServiceError(message=f"Authentication error: {str(e)}", name="Authentication")
