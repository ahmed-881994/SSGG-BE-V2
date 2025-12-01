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
                "id": permission.permission_id,
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
            
    def search_permissions(self, name: str | None, category: str | None) -> Dict | None:
        """
        Search permissions by name and/or category.
        """
        try:
            permissions = self.permission_repository.search_permissions(name, category)
            if not permissions:
                raise EntityDoesNotExistError(
                    message="No permissions found matching the criteria",
                    name="Permissions Not Found"
                )
            result = []
            for permission in permissions:
                result.append({
                    "id": permission.permission_id,
                    "name": permission.name,
                    "display_name": permission.display_name,
                    "description": permission.description,
                    "category": permission.category,
                    "is_active": permission.is_active,
                    "created_at": permission.created_at,
                    "updated_at": permission.updated_at
                })
            return {"permissions": result}
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error while searching permissions: {str(e)}")
            raise ServiceError(
                message="An unexpected error occurred while searching for permissions",
                name="Unexpected Error"
            )
            
    def create_permission(self, permission_data: dict) -> Dict:
        """
        Create a new permission.
        """
        try:
            permission = self.permission_repository.get_permission_by_name(permission_data['name'])
            if permission:
                raise EntityAlreadyExistsError(
                    message=f"Permission with name {permission_data['name']} already exists",
                    name="Permission Already Exists"
                )
            new_permission = self.permission_repository.create_permission(**permission_data)
            return {
                "id": new_permission.permission_id,
                "name": new_permission.name,
                "display_name": new_permission.display_name,
                "description": new_permission.description,
                "category": new_permission.category,
                "is_active": new_permission.is_active,
                "created_at": new_permission.created_at,
                "updated_at": new_permission.updated_at
            }
        except EntityAlreadyExistsError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error while creating permission: {str(e)}")
            raise ServiceError(
                message="An unexpected error occurred while creating the permission",
                name="Unexpected Error"
            )
            
    def update_permission(self, permission_id: int, update_data: dict) -> Dict:
        """
        Update an existing permission.
        """
        try:
            permission = self.permission_repository.get_permission_by_permission_id(permission_id)
            if not permission:
                raise EntityDoesNotExistError(
                    message=f"Permission with ID {permission_id} does not exist",
                    name="Permission Not Found"
                )
            updated_permission = self.permission_repository.update_permission(permission, update_data)
            return {
                "id": updated_permission.permission_id,
                "name": updated_permission.name,
                "display_name": updated_permission.display_name,
                "description": updated_permission.description,
                "category": updated_permission.category,
                "is_active": updated_permission.is_active,
                "created_at": updated_permission.created_at,
                "updated_at": updated_permission.updated_at
            }
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error while updating permission ID {permission_id}: {str(e)}")
            raise ServiceError(
                message="An unexpected error occurred while updating the permission",
                name="Unexpected Error"
            )
            
    def delete_permission(self, permission_id: int) -> None:
        """
        Delete a permission by its ID.
        """
        try:
            permission = self.permission_repository.get_permission_by_permission_id(permission_id)
            if not permission:
                raise EntityDoesNotExistError(
                    message=f"Permission with ID {permission_id} does not exist",
                    name="Permission Not Found"
                )
            self.permission_repository.delete_permission(permission)
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error while deleting permission ID {permission_id}: {str(e)}")
            raise ServiceError(
                message="An unexpected error occurred while deleting the permission",
                name="Unexpected Error"
            )