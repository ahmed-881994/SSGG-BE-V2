from typing import Dict, List

from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.exceptions import (EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.models.role_model import Role
from app.repositories.role_repository import RoleRepository


class RoleService:
    """Service class for Role business logic operations."""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.role_repository = RoleRepository(db_session)

    def get_role_by_id(self, id: int) -> Dict | None:
        """
        Retrieve a role by its ID.
        """
        try:
            role = self.role_repository.get_role_by_id(id)
            if not role:
                logger.warning(f"Role not found: {id}")
                raise EntityDoesNotExistError(
                    f"Role with ID {id} does not exist.", name="Role Retrieval Error")
            return{
                "id": role.id,
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "is_system_role": role.is_system_role,
                "is_active": role.is_active,
                "created_at": role.created_at,
                "updated_at": role.updated_at,
                "permissions": role.permissions
            }
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving role: {id}: {str(e)}")
            raise ServiceError(
                message=f"Failed to retrieve role: {str(e)}",
                name="Role Retrieval Error"
            )
            
    def search_roles(self, role_id: int | None = None, role_name: str | None = None) -> Dict|None:
        """
        Search roles by ID and/or name.
        """
        try:
            roles = self.role_repository.search_roles(role_id, role_name)
            if not roles:
                logger.warning(f"Role not found: {id}")
                raise EntityDoesNotExistError(
                    f"Role with ID {id} does not exist.", name="Role Retrieval Error")
            result = []
            for role in roles:
                result.append({
                    "id": role.id,
                    "name": role.name,
                    "display_name": role.display_name,
                    "description": role.description,
                    "is_system_role": role.is_system_role,
                    "is_active": role.is_active,
                    "created_at": role.created_at,
                    "updated_at": role.updated_at,
                    # "permissions": role.permissions
                })
            return {"roles": result}
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error searching roles: {str(e)}")
            raise ServiceError(
                message=f"Failed to search roles: {str(e)}",
                name="Role Search Error"
            )
    def create_role(self, role_data) -> Dict | None:
        """
        Create a new role.
        """
        try:
            role = self.role_repository.get_role_by_name(role_data['name'])
            if role:
                logger.warning(f"Role already exists with name: {role_data['name']}")
                raise EntityAlreadyExistsError(
                    message=f"Role with name {role_data['name']} already exists.",
                    name="Role Creation Error"
                )
            role = self.role_repository.create_role(**role_data)
            return{
                "id": role.id,
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "is_system_role": role.is_system_role,
                "is_active": role.is_active,
                "created_at": role.created_at,
                "updated_at": role.updated_at,
                "permissions": role.permissions
            }
        except EntityAlreadyExistsError:
            raise
        except Exception as e:
            logger.error(f"Error creating role: {str(e)}")
            raise ServiceError(
                message=f"Failed to create role: {str(e)}",
                name="Role Creation Error"
            )
            
    def update_role(self, role_id: int, update_data: Dict) -> Dict | None:
        """
        Update an existing role.
        """
        try:
            role = self.role_repository.get_role_by_id(role_id)
            if not role:
                logger.warning(f"Role not found: {role_id}")
                raise EntityDoesNotExistError(
                    f"Role with ID {role_id} does not exist.", name="Role Update Error")
            role = self.role_repository.update_role(
                role,
                name=update_data.get('name', role.name),
                display_name=update_data.get('display_name', role.display_name),
                description=update_data.get('description', role.description),
                is_system_role=update_data.get('is_system_role', role.is_system_role),
                is_active=update_data.get('is_active', role.is_active)
            )
            return{
                "id": role.id,
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "is_system_role": role.is_system_role,
                "is_active": role.is_active,
                "created_at": role.created_at,
                "updated_at": role.updated_at,
                "permissions": role.permissions
            }
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error updating role: {str(e)}")
            raise ServiceError(
                message=f"Failed to update role: {str(e)}",
                name="Role Update Error"
            )
            
    def delete_role(self, role_id: int) -> None:
        """
        Delete an existing role.
        """
        try:
            role = self.role_repository.get_role_by_id(role_id)
            if not role:
                logger.warning(f"Role not found: {role_id}")
                raise EntityDoesNotExistError(
                    f"Role with ID {role_id} does not exist.", name="Role Deletion Error")
            self.role_repository.delete_role(role)
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error deleting role: {str(e)}")
            raise ServiceError(
                message=f"Failed to delete role: {str(e)}",
                name="Role Deletion Error"
            )