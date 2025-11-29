from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.exceptions import ServiceError
from app.models.role_model import Role
from app.models.role_permission_model import RolePermission
from app.repositories.base_repository import BaseRepository
from app.util.egy_time import get_egypt_time


class RoleRepository(BaseRepository[Role]):
    """
    Repository for Role model, providing CRUD operations.
    """
    
    def __init__(self, db: Session):
        super().__init__(db, Role)

    def get_role_by_id(self, id: int) -> Role | None:
        """
        Retrieve a role by its ID.
        """
        try:
            return self.db.query(Role).filter(Role.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving role by ID {id}: {e}")
            raise ServiceError(message=f"Failed to retrieve role: {str(e)}",
                name="Database Error")
            
    def get_role_by_name(self, name: str) -> Role | None:
        """
        Retrieve a role by its name.
        """
        try:
            return self.db.query(Role).filter(Role.name == name).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving role by name {name}: {e}")
            raise ServiceError(message=f"Failed to retrieve role: {str(e)}",
                name="Database Error")
            
    def search_roles(self, role_id: int | None = None, role_name: str | None = None) -> list[Role]|None:
        """
        Search roles by ID and/or name.
        """
        try:
            query = self.db.query(Role)
            if role_id is not None:
                query = query.filter(Role.id == role_id)
            if role_name is not None:
                query = query.filter(Role.name.ilike(f"%{role_name}%"))
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error searching roles: {e}")
            raise ServiceError(message=f"Failed to search roles: {str(e)}",
                name="Database Error")
            
    def create_role(self, name: str, display_name: str, description: str, is_system_role: bool) -> Role:
        """
        Create a new role.
        """
        try:
            new_role = Role()
            new_role.name= name
            new_role.display_name= display_name
            new_role.description= description
            new_role.is_system_role= is_system_role
            new_role.created_at= get_egypt_time()
            self.db.add(new_role)
            self.db.commit()
            self.db.refresh(new_role)
            return new_role
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating role: {e}")
            raise ServiceError(message=f"Failed to create role: {str(e)}",
                name="Database Error")
            
    def update_role(self, role: Role, name: str, display_name: str, description: str, is_system_role: bool, is_active: bool) -> Role:
        """
        Update an existing role.
        """
        try:
            role.name = name
            role.display_name = display_name
            role.description = description
            role.is_system_role = is_system_role
            role.is_active = is_active
            role.updated_at = get_egypt_time()
            self.db.commit()
            self.db.refresh(role)
            return role
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating role ID {role.id}: {e}")
            raise ServiceError(message=f"Failed to update role: {str(e)}",
                name="Database Error")
            
    def delete_role(self, role: Role) -> None:
        """
        Delete a role by its ID.
        """
        try:
            # Delete existing role-permission associations
            self.db.query(RolePermission).filter(
                RolePermission.role_id == role.id
            ).delete(synchronize_session=False)
            self.db.delete(role)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting role ID {role.id}: {e}")
            raise ServiceError(message=f"Failed to delete role: {str(e)}",
                name="Database Error")
            
    def update_role_permissions(self, role: Role, permissions: list, user_id: int) -> Role:
        """
        Add permissions to a role.
        """
        try:
            # Delete existing role-permission associations
            self.db.query(RolePermission).filter(
                RolePermission.role_id == role.id
            ).delete(synchronize_session=False)
            
            # Create new associations with current timestamp
            current_time = get_egypt_time()
            for permission in permissions:
                role_permission = RolePermission()
                role_permission.role_id = role.id
                role_permission.permission_id = permission.id
                role_permission.created_at = current_time
                role_permission.created_by = user_id
                self.db.add(role_permission)
            
            # Update role's updated_at
            role.updated_at = current_time
            self.db.commit()
            self.db.refresh(role)
            return role
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error adding permissions to role ID {role.id}: {e}")
            raise ServiceError(message=f"Failed to add permissions: {str(e)}",
                name="Database Error")