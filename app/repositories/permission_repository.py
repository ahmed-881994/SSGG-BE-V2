from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.exceptions import ServiceError
from app.models.permission_model import Permission
from app.models.role_permission_model import RolePermission
from app.repositories.base_repository import BaseRepository
from app.util.egy_time import get_egypt_time


class PermissionRepository(BaseRepository[Permission]):
    """
    Repository for Permission model, providing CRUD operations.
    """
    
    def __init__(self, db: Session):
        super().__init__(db, Permission)
        
    def _get_next_permission_id(self) -> int:
        """Get the next available permission ID."""
        try:
            return (self.db.query(func.max(Permission.permission_id)).scalar() or 0) + 1
        except SQLAlchemyError as e:
            raise ServiceError(
                message=f"Failed to retrieve next permission ID: {str(e)}",
                name="Database Error"
            )
        
    def get_permission_by_name(self, name: str) -> Permission | None:
        """
        Retrieve a permission by its name.
        """
        try:
            return self.db.query(Permission).filter(Permission.name == name).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving permission by name {name}: {e}")
            raise ServiceError(message=f"Failed to retrieve permission: {str(e)}",
                name="Database Error")    
    
    def get_permission_by_permission_id(self, id: int) -> Permission | None:
        """
        Retrieve a permission by its ID.
        """
        try:
            return self.db.query(Permission).filter(Permission.permission_id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving permission by ID {id}: {e}")
            raise ServiceError(message=f"Failed to retrieve permission: {str(e)}",
                name="Database Error")
            
    def search_permissions(self, name: str | None, category: str | None) -> list[Permission]|None:
        """
        Search permissions by name.
        """
        try:
            query = self.db.query(Permission)
            if name is not None:
                query = query.filter(or_(Permission.name.ilike(f"%{name}%"), Permission.display_name.ilike(f"%{name}%")))
            if category is not None:
                query = query.filter(Permission.category.ilike(f"%{category}%"))
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error searching permissions with name {name}: {e}")
            raise ServiceError(message=f"Failed to search permissions: {str(e)}",
                name="Database Error")
            
    def create_permission(self, name: str, display_name: str, description: str = '', category: str = '') -> Permission:
        """
        Create a new permission.
        """
        try:
            new_permission_id = self._get_next_permission_id()
            new_permission = Permission()
            new_permission.permission_id = new_permission_id
            new_permission.name = name
            new_permission.display_name = display_name
            new_permission.description = description
            new_permission.category = category
            new_permission.created_at = get_egypt_time()
            
            self.db.add(new_permission)
            self.db.commit()
            self.db.refresh(new_permission)
            return new_permission
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating permission: {e}")
            raise ServiceError(message=f"Failed to create permission: {str(e)}",
                name="Database Error")
            
    def update_permission(self, permission: Permission, update_data: dict) -> Permission:
        """
        Update an existing permission.
        """
        try:
            permission.name = update_data.get('name', permission.name)
            permission.display_name = update_data.get('display_name', permission.display_name)
            permission.description = update_data.get('description', permission.description)
            permission.category = update_data.get('category', permission.category)
            permission.is_active = update_data.get('is_active', permission.is_active)
            permission.updated_at = get_egypt_time()
            
            self.db.commit()
            self.db.refresh(permission)
            return permission
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating permission ID {permission.permission_id}: {e}")
            raise ServiceError(message=f"Failed to update permission: {str(e)}",
                name="Database Error")
            
    def delete_permission(self, permission: Permission) -> None:
        """
        Delete a permission by its ID.
        """
        try:
            # Delete existing role-permission associations
            self.db.query(RolePermission).filter(
                RolePermission.permission_id == permission.permission_id
            ).delete(synchronize_session=False)
            self.db.delete(permission)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting permission ID {permission.permission_id}: {e}")
            raise ServiceError(message=f"Failed to delete permission: {str(e)}",
                name="Database Error")