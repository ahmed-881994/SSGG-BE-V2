from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.database import get_db_session
from app.core.dependencies import get_user_in_token
from app.core.exceptions import (EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/permissions", tags=["Permissions"], dependencies=[Depends(get_user_in_token)])

@router.post("", tags=["Permissions"], status_code=201)
def create_permission():
    """
    Create a new permission
    """
    pass  # Implementation goes here

@router.get("/{permission_id}", tags=["Permissions"])
def get_permission(permission_id: int, db: Session = Depends(get_db_session)):
    """
    Get permission by ID
    """
    try:
        permission_service = PermissionService(db)
        return permission_service.get_permission_by_permission_id(permission_id)
    except EntityDoesNotExistError as e:
        logger.error(f"Permission not found: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail=f"Permission not found")
    except ServiceError as e:
        logger.error(f"Service error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail='Service error')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Unexpected error')

@router.put("/{permission_id}", tags=["Permissions"])
def update_permission(permission_id: int, permission_data: dict, db: Session = Depends(get_db_session)):
    """
    Update permission by ID
    """
    pass  # Implementation goes here

@router.delete("/{permission_id}", tags=["Permissions"], status_code=204)
def delete_permission(permission_id: int, db: Session = Depends(get_db_session)):
    """
    Delete permission by ID
    """
    pass  # Implementation goes here

@router.get("", tags=["Permissions"])
def search_permissions(name: Optional[str] = None, db: Session = Depends(get_db_session)):
    """
    Search permissions
    """
    pass  # Implementation goes here