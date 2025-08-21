"""
Authentication Service Module

Centralized authentication service handling user authentication,
user retrieval, and validation operations.
"""
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.exceptions import (AuthenticationFailed, EntityDoesNotExistError,
                                 ServiceError)
from app.models.user_model import User
from app.services.user_service import UserService
from app.util.password import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
class AuthService:
    """Centralized authentication service"""

    def __init__(self, db_session: Session):
        """Initialize AuthService with database session."""
        self.db_session = db_session

    def authenticate_user(self, login: str, password: str) -> User:
        """
        Authenticate user with login and password

        Args:
            login: The login (username or user ID) to authenticate
            password: The plain text password to verify
            
        Returns:
            Optional[User]: User object if authentication successful, None otherwise

        Raises:
            AuthenticationFailed: If authentication fails
        """
        logger.info(f"Attempting authentication for user: {login}")
        # start_time = time.time()
        
        try:
            user_service = UserService(self.db_session)
            user = user_service.get_user_by_login(login=login)
            if not user:
                logger.warning(f"Authentication failed: User '{login}' not found")
                raise AuthenticationFailed(
                    message="User not found",
                    name="Authentication"
                )
            
            if not verify_password(password, user.password_hash, user.salt):
                logger.warning(f"Authentication failed: Invalid password for user '{login}'")
                raise AuthenticationFailed(
                    message="Invalid password",
                    name="Authentication"
                )
                
            # auth_time = round((time.time() - start_time) * 1000, 2)
            # logger.info(f"Authentication successful for user '{login}' in {auth_time}ms")
            return user
            
        except EntityDoesNotExistError:
            logger.warning(f"Authentication failed: User '{login}' not found")
            raise AuthenticationFailed(
                message="User not found",
                name="Authentication"
            )
        except Exception as e:
            # auth_time = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Authentication error for user '{login}': {str(e)}", exc_info=True)
            raise ServiceError(message=f"Authentication error: {str(e)}", name="Authentication")