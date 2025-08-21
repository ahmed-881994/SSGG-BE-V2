from __future__ import annotations

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    password_reset: Mapped[bool] = mapped_column(default=False)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    salt: Mapped[str] = mapped_column(String(100), nullable=False)
    # date_created: Mapped[Date] = mapped_column(Date, nullable=False)
    # date_updated: Mapped[Date] = mapped_column(Date, nullable=False)

    
    def __repr__(self):
        return f"<User(id={self.id}, user_name={self.user_name}, is_active={self.is_active})>"
    
    
    def to_dict(self):
        """Convert User instance to dictionary.
        
        Note: Excludes sensitive information like password_hash and salt.
        """
        return {
            "id": self.id,
            "user_name": self.user_name,
            "user_id": self.user_id,
            "is_active": self.is_active,
            "password_reset": self.password_reset,
            # "user_type": self.user_type
        }

    def to_dict_with_auth(self):
        """Convert User instance to dictionary including authentication fields.
        
        WARNING: This includes sensitive authentication data.
        Only use when necessary for authentication operations.
        """
        return {
            "id": self.id,
            "user_name": self.user_name,
            "user_id": self.user_id,
            "password_hash": self.password_hash,
            "salt": self.salt,
            "is_active": self.is_active,
            "password_reset": self.password_reset,
            # "user_type": self.user_type
        }

    @staticmethod
    def strip_sensitive_info(user_obj: User) -> User:
        """Create a copy of User instance without sensitive information."""
        # Create a new user object without sensitive data
        clean_user = User(
            id=user_obj.id,
            user_name=user_obj.user_name,
            user_id=user_obj.user_id,
            is_active=user_obj.is_active,
            password_reset=user_obj.password_reset,
            password_hash="",  # Empty values instead of deleting
            salt=""
        )
        return clean_user