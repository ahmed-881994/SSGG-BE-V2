from typing import Dict

from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.exceptions import (EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.repositories.permission_repository import PermissionRepository

class PermissionService:
    """Service class for Permission business logic operations."""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.permission_repository = PermissionRepository(db_session)
        
    def get_permission_by_permission_id(self, id: int) -> Dict | None:
        """
        Retrieve a permission by its ID.
        """
        try:
            permission = self.permission_repository.get_permission_by_permission_id(id)
            if not permission:
                logger.warning(f"Permission not found: {id}")
                raise EntityDoesNotExistError(
                    message=f"Permission with ID {id} does not exist",
                    name="Permission Not Found"
                )
            return {
                "permission_id": permission.permission_id,
                "name": permission.name,
                "display_name": permission.display_name,
                "description": permission.description,
                "category": permission.category,
                "is_active": permission.is_active,
                "created_at": permission.created_at,
                "updated_at": permission.updated_at
            }
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error while retrieving permission by permission ID {id}: {str(e)}")
            raise ServiceError(
                message="An unexpected error occurred while retrieving the permission",
                name="Unexpected Error"
            )