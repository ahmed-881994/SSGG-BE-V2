from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.exceptions import ServiceError
from app.models.permission_model import Permission
from app.repositories.base_repository import BaseRepository
from app.util.egy_time import get_egypt_time


class PermissionRepository(BaseRepository[Permission]):
    """
    Repository for Permission model, providing CRUD operations.
    """
    
    def __init__(self, db: Session):
        super().__init__(db, Permission)
        
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