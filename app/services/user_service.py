from typing import List, Optional

from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.exceptions import (EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.models.user_model import User
from app.repositories.user_repository import UserRepository
from app.services.email_templates import email_templates
from app.services.email_service import email_service
from app.util.password import (generate_random_password, generate_salt,
                               get_password_hash)


class UserService:
    """Service class for User business logic operations."""
    
    def __init__(self, db_session: Session):
        """Initialize UserService with database session."""
        self.user_repository = UserRepository(db_session)
        self.db_session = db_session
        
    def get_user_by_id(self, id: int) -> User:
        """Get user by database ID.
        
        Args:
            user_id: Database ID of the user
            
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
            logger.error(f"Error retrieving user {id}: {str(e)}", exc_info=True)
            raise ServiceError(
                message=f"Failed to retrieve user: {str(e)}",
                name="User Retrieval Error"
            )

    def get_user_by_user_id(self, user_id: str) -> User:
        """Get user by database ID.
        
        Args:
            user_id: Database ID of the user
            
        Returns:
            User: User instance
            
        Raises:
            EntityDoesNotExistError: If user not found
            ServiceError: If retrieval fails
        """
        try:
            user = self.user_repository.get_user_by_user_id(user_id)
            return user
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {str(e)}", exc_info=True)
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
            logger.error(f"Error searching users: {str(e)}", exc_info=True)
            raise ServiceError(
                message=f"Failed to search users: {str(e)}",
                name="User Search Error"
            )

            
    def search_users(self, user_name: Optional[str] = None, user_id: Optional[str] = None) -> dict[str, list[User]]:
        """Search for users by name or ID.
        
        Args:
            user_name: Optional username to search for (partial match)
            user_id: Optional external user ID to search for (partial match)
            
        Returns:
            dict[str, list[User]]: Dictionary containing a list of matching users
            
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
            logger.error(f"Error searching users: {str(e)}", exc_info=True)
            raise ServiceError(
                message=f"Failed to search users: {str(e)}",
                name="User Search Error"
            )

    def update_user(self, user_id: str, **kwargs) -> User:
        """Update user information.
        
        Args:
            user_id: ID of user to update
            **kwargs: Fields to update
            
        Returns:
            User: Updated user instance
            
        Raises:
            EntityDoesNotExistError: If user not found
            ServiceError: If update fails
        """
        try:
            user = self.user_repository.update_user(user_id, **kwargs)
            return user
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}", exc_info=True)
            raise ServiceError(
                message=f"Failed to update user: {str(e)}",
                name="User Update Error"
            )

    def delete_user(self, user_id: str) -> bool:
        """Delete a user from the database.
        
        Args:
            user_id: ID of user to delete
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            EntityDoesNotExistError: If user not found
            ServiceError: If deletion fails
        """
        try:
            return self.user_repository.delete_user(user_id=user_id)
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}", exc_info=True)
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
            logger.info(f"Creating user")
            # Generate password
            new_password = generate_random_password()
            logger.info(f"Generated random password for new user")
            # Generate salt and hash password
            salt = generate_salt()
            hashed_password, _ = get_password_hash(new_password, salt)
            logger.info(f"Password hashed successfully for new user")
            # Store hashed password and salt in user_data
            user_data['password_hash'] = hashed_password
            user_data['salt'] = salt
            user_data.pop('password', None)  # Remove plain password safely
            user = self.user_repository.create_user(**user_data)
            logger.info(f"User {user.user_id} created successfully")
            
            email = email_templates.welcome_email(
                user_name=user.user_name,
                user_id=user.user_id,
                temporary_password=new_password
            )
            
            email_service.send_email(
                to_email=user.email,
                subject=email.subject,
                body=email.text_body,
                html_body=email.html_body
            )
            logger.info(f"Welcome email sent to user {user.user_id}")
            return user
        except EntityAlreadyExistsError:
            logger.warning(f"Attempted to create user with existing username or user ID: {user_data.get('user_name')} / {user_data.get('user_id')}")
            raise
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}", exc_info=True)
            raise ServiceError(
                message=f"Failed to create user",
                name="User Creation Error"
            )

    def update_user_password(self, user_id: str, new_password: str, old_password: str) -> bool:
        """Update a user's password.

        Args:
            user_id (str): ID of the user to update.
            new_password (str): New password to set.
            old_password (str): Current password for verification.

        Returns:
            bool: True if updated successfully

        Raises:
            EntityDoesNotExistError: If user not found
            ServiceError: If update fails
        """
        try:
            logger.info(f"Updating password for user {user_id}")
            user = self.user_repository.get_user_auth(user_id)
            # Verify old password
            old_password_hash, _ = get_password_hash(old_password, user.salt)
            if not old_password_hash == user.password_hash:
                logger.warning(f"Old password verification failed for user {user_id}")
                raise ServiceError(
                    message="Old password is incorrect.",
                    name="User Password Update Error"
                )
            # Generate new salt and hash password
            salt = generate_salt()
            hashed_password, _ = get_password_hash(new_password, salt)
            user = self.user_repository.update_user(
                user_id,
                password_hash=hashed_password,
                salt=salt
            )
            logger.info(f"Password for user {user_id} updated successfully")
            return True
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error updating password for user {user_id}: {str(e)}", exc_info=True)
            raise ServiceError(
                message=f"Failed to update user password: {str(e)}",
                name="User Password Update Error"
            )
            
    def reset_user_password(self, user_id: str) -> bool:
        """Reset a user's password.

        Args:
            user_id (str): ID of the user to reset.

        Returns:
            bool: True if reset successfully

        Raises:
            EntityDoesNotExistError: If user not found
            ServiceError: If reset fails
        """
        try:
            logger.info(f"Resetting password for user {user_id}")
            user = self.user_repository.get_user_auth(user_id)
            # Generate new password
            new_password = generate_random_password()
            # Hash new password
            hashed_password, salt = get_password_hash(new_password)
            user = self.user_repository.update_user(
                user.user_id,
                password_hash=hashed_password,
                password_reset=True,
                salt=salt
            )
            logger.info(f"Password for user {user_id} reset successfully")
            # Send email with new password
            email = email_templates.password_reset_email(
                user_name=user.user_name,
                new_password=new_password
            )
            
            email_service.send_email(
                to_email=user.email,
                subject=email.subject,
                body=email.text_body,
                html_body=email.html_body
            )
            logger.info(f"Password reset email sent to user {user_id}")
            return True
        except EntityDoesNotExistError:
            logger.warning(f"Attempted to reset password for non-existent user {user_id}")
            raise
        except Exception as e:
            logger.error(f"Error resetting password for user {user_id}: {str(e)}", exc_info=True)
            raise ServiceError(
                message=f"Failed to reset user password: {str(e)}",
                name="User Password Reset Error"
            )
            
    def get_user_permissions_by_id(self, id:int)-> List[str]:
        
        try:
            logger.info(f"Retrieving permissions for user {id}")
            user = self.get_user_by_id(id)
            
            if user.role is None:
                logger.warning(f"User {id} has no role assigned, returning empty permissions list")
                return []
            user_permissions = [permission.name for permission in user.role.permissions]
            logger.info(f"Successfully retrieved permissions for user {id}")
            return user_permissions
            # if user_permissions:
            #     return user_permissions
            # else:
            #     return []
            
        except EntityDoesNotExistError:
            logger.warning(f"Attempted to retrieve permissions for non-existent user {id}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving permissions for user {id}: {str(e)}", exc_info=True)
            raise ServiceError(
                message=f"Failed to retrieve user permissions: {str(e)}",
                name="User Permissions Retrieval Error"
            )