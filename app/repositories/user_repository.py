from typing import Optional

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.models.user_model import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User database operations."""

    def __init__(self, db_session: Session):
        """Initialize UserRepository with database session."""
        super().__init__(db_session, User)


    def get_user_by_id(self, id: int) -> User:
        """Get user by ID."""
        try:
            user = self.db.query(User).filter(User.id == id).first()
            if not user:
                raise EntityDoesNotExistError(
                    message=f"User with ID {id} not found",
                    name="User Retrieval Error"
                )
            return User.strip_sensitive_info(user)
        except SQLAlchemyError as e:
            raise ServiceError(
                message=f"Failed to retrieve user: {str(e)}",
                name="Database Error"
            )

    def get_user_by_user_id(self, user_id: str) -> User:
        """Get user by ID."""
        try:
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise EntityDoesNotExistError(
                    message=f"User with ID {user_id} not found",
                    name="User Retrieval Error"
                )
            return User.strip_sensitive_info(user)
        except SQLAlchemyError as e:
            raise ServiceError(
                message=f"Failed to retrieve user: {str(e)}",
                name="Database Error"
            )

    def get_user_auth(self, login: str) -> User:
        """Search for users by a query string."""
        try:
            # Create a base query
            query = self.db.query(User)
            query = query.filter(
                or_(User.user_name == login, User.user_id == login))
            user = query.first()
            if not user:
                raise EntityDoesNotExistError(
                    message=f"User with login {login} not found",
                    name="User Auth Retrieval Error"
                )
            return user
        except SQLAlchemyError as e:
            raise ServiceError(
                message=f"Failed to retrieve user: {str(e)}",
                name="Database Error"
            )

    def search_users(self, user_name: Optional[str] = None, user_id: Optional[str] = None) -> dict[str, list[User]]:
        """Search for users by a query string."""
        try:
            # Create a base query
            query = self.db.query(User)

            # Apply filters if provided
            filters = []
            if user_name:
                filters.append(User.user_name.ilike(f"%{user_name}%"))
            if user_id:
                filters.append(User.user_id.ilike(f"%{user_id}%"))
                
            # if not filters:
            #     raise InvalidOperationError(
            #         message="At least one search criteria must be provided",
            #         name="User Search Error"
            #     )

            users = query.filter(or_(*filters)).all()

            if not users:
                raise EntityDoesNotExistError(
                    message="No users found with the provided criteria",
                    name="User Search Error"
                )

            return {'users': [User.strip_sensitive_info(user) for user in users]}
        except SQLAlchemyError as e:
            raise ServiceError(
                message=f"Failed to search users: {str(e)}",
                name="Database Error"
            )
    
    def update_user(self, user_id: str, **kwargs) -> User:
        """
        Update fields of a user with the given ID.

        Parameters:
            id (int): The ID of the user to update.
            **kwargs: Arbitrary keyword arguments representing fields to update.

        Returns:
            User: The updated user object with sensitive information stripped.

        Raises:
            EntityDoesNotExistError: If the user with the given ID does not exist.
            ServiceError: If a database error occurs during the update.
        """
        try:
            
            user_with_same_username = None
            if 'user_name' in kwargs:
                user_with_same_username = self.db.query(User).filter(
                    User.user_name == kwargs['user_name'],
                    User.user_id != user_id
                ).first()
            if user_with_same_username:
                raise EntityAlreadyExistsError(
                    message="User with this username already exists.",
                    name="User Update Error"
                )
            
            user = self.db.query(User).filter(User.user_id == user_id).first()

            if not user:
                raise EntityDoesNotExistError(
                    message=f"User with ID {user_id} not found",
                    name="User Update Error"
                )

            # Update provided fields
            for field, value in kwargs.items():
                if hasattr(user, field):
                    setattr(user, field, value)

            updated_user = super().update(user)

            return User.strip_sensitive_info(updated_user)

        except SQLAlchemyError as e:
            self.db.rollback()
            raise ServiceError(
                message=f"Failed to update user: {str(e)}",
                name="Database Error"
            )

    def delete_user(self, user_id: str) -> bool:
        """Delete a user by user ID."""
        try:
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise EntityDoesNotExistError(
                    message=f"User with ID {user_id} not found",
                    name="User Delete Error"
                )
            return super().delete(user)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ServiceError(
                message=f"Failed to delete user: {str(e)}",
                name="Database Error"
            )

    def create_user(self, user_name: str, user_id: str, email: str, password_hash: str,
                    role_id: int, 
                    salt: str, is_active: bool = True) -> User:
        """Create a new user in the database.

        Args:
            user_name: Unique username for login
            user_id: Optional external user identifier
            email: User's email address
            password_hash: Hashed password
            user_type: Type of user (1=Super user, 2=General Leader, etc.)
            salt: Password salt
            is_active: Whether user account is active

        Returns:
            User: Created user instance

        Raises:
            ServiceError: If user creation fails
        """
        try:

            # Create a base query
            query = self.db.query(User)

            # Apply filters if provided
            filters = []
            if user_name:
                filters.append(User.user_name == user_name)
            if user_id:
                filters.append(User.user_id == user_id)

            # Check if user already exists
            existing_user = query.filter(or_(*filters)).count()
            if existing_user > 0:
                raise EntityAlreadyExistsError(
                    message="User with this username or user ID already exists.",
                    name="User Creation Error"
                )

            user = User()
            user.user_name = user_name
            user.user_id = user_id
            user.email = email
            user.password_hash = password_hash
            user.role_id = role_id
            user.salt = salt
            user.is_active = is_active
            user.password_reset = True

            super().create(user)

            return User.strip_sensitive_info(user)

        except SQLAlchemyError as e:
            self.db.rollback()
            raise ServiceError(message=f"Failed to create user: {str(e)}",name="Database Error")
