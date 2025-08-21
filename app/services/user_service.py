from typing import Optional

from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.exceptions import (EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.models.user_model import User
from app.repositories.user_repository import UserRepository
from app.util.password import generate_salt, get_password_hash


class UserService:
    """Service class for User business logic operations."""
    
    def __init__(self, db_session: Session):
        """Initialize UserService with database session."""
        self.user_repository = UserRepository(db_session)
        self.db_session = db_session
        
    def get_user_by_id(self, id: int) -> User:
        """Get user by database ID.
        
        Args:
            id: Database ID of the user
            
        Returns:
            User: User instance
            
        Raises:
            EntityDoesNotExistError: If user not found
            ServiceError: If retrieval fails
        """
        try:
            user = self.user_repository.get_user_by_id(id)
            return user
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving user {id}: {str(e)}")
            raise ServiceError(
                message=f"Failed to retrieve user: {str(e)}",
                name="User Retrieval Error"
            )

    def get_user_by_login(self, login: str) -> User:
        """Get user authentication information.

        Args:
            login (str): Login identifier (username or user ID) of the user.

        Returns:
            User: User instance

        Raises:
            EntityDoesNotExistError: If user not found
            ServiceError: If retrieval fails
        """
        try:
            user = self.user_repository.get_user_auth(login=login)
            return user
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error searching users: {str(e)}")
            raise ServiceError(
                message=f"Failed to search users: {str(e)}",
                name="User Search Error"
            )

            
    def search_users(self, user_name: Optional[str] = None, user_id: Optional[str] = None) -> list[User]:
        """Search for users by name or ID.
        
        Args:
            user_name: Optional username to search for (partial match)
            user_id: Optional external user ID to search for (partial match)
            
        Returns:
            List[User]: List of matching users
            
        Raises:
            EntityDoesNotExistError: If no users found
            ServiceError: If search fails
        """
        try:
            users = self.user_repository.search_users(user_name=user_name, user_id=user_id)
            return users
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error searching users: {str(e)}")
            raise ServiceError(
                message=f"Failed to search users: {str(e)}",
                name="User Search Error"
            )

    def update_user(self, id: int, **kwargs) -> User:
        """Update user information.
        
        Args:
            id: Database ID of user to update
            **kwargs: Fields to update
            
        Returns:
            User: Updated user instance
            
        Raises:
            EntityDoesNotExistError: If user not found
            ServiceError: If update fails
        """
        try:
            user = self.user_repository.update_user(id, **kwargs)
            return user
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error updating user {id}: {str(e)}")
            raise ServiceError(
                message=f"Failed to update user: {str(e)}",
                name="User Update Error"
            )

    def delete_user(self, id: int) -> bool:
        """Delete a user from the database.
        
        Args:
            id: Database ID of user to delete
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            EntityDoesNotExistError: If user not found
            ServiceError: If deletion fails
        """
        try:
            return self.user_repository.delete_user(id)
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error deleting user {id}: {str(e)}")
            raise ServiceError(
                message=f"Failed to delete user: {str(e)}",
                name="User Deletion Error"
            )

    def create_user(self, user_data: dict) -> User:
        """Create a new user.

        Args:
            user_data (dict): User data to create.

        Returns:
            User: User instance

        Raises:
            ServiceError: If user creation fails.
        """
        try:
            # Generate salt and hash password
            salt = generate_salt()
            hashed_password, _ = get_password_hash(user_data['password'], salt)
            # Store hashed password and salt in user_data
            user_data['password_hash'] = hashed_password
            user_data['salt'] = salt
            user_data.pop('password', None)  # Remove plain password safely
            user = self.user_repository.create_user(**user_data)
            return user
        except EntityAlreadyExistsError:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise ServiceError(
                message=f"Failed to create user: {str(e)}",
                name="User Creation Error"
            )