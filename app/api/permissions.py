from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.database import get_db_session
from app.core.dependencies import get_user_in_token
from app.core.exceptions import (EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.schemas.permission_schema import PermissionCreate, PermissionListResponse, PermissionResponse, PermissionUpdate
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/permissions", tags=["Permissions"], dependencies=[Depends(get_user_in_token)])

@router.post("", tags=["Permissions"], status_code=201, response_model=PermissionResponse)
def create_permission(permission_data: PermissionCreate, db: Session = Depends(get_db_session)):
    """
    Create a new permission
    """
    try:
        permission_service = PermissionService(db)
        return permission_service.create_permission(permission_data.model_dump())
    except EntityAlreadyExistsError as e:
        logger.error(f"Permission already exists: {e.message}", exc_info=True)
        raise HTTPException(status_code=400, detail="Permission already exists")
    except ServiceError as e:
        logger.error(f"Service error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail='Service error')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Unexpected error')

@router.get("/{permission_id}", tags=["Permissions"], response_model=PermissionResponse)
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

@router.put("/{permission_id}", tags=["Permissions"], response_model=PermissionResponse)
def update_permission(permission_id: int, permission_data: PermissionUpdate, db: Session = Depends(get_db_session)):
    """
    Update permission by ID
    """
    try:
        permission_service = PermissionService(db)
        return permission_service.update_permission(permission_id, permission_data.model_dump(exclude_none=True))
    except EntityDoesNotExistError as e:
        logger.error(f"Permission not found: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail="Permission not found")
    except ServiceError as e:
        logger.error(f"Service error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail='Service error')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Unexpected error')

@router.delete("/{permission_id}", tags=["Permissions"], status_code=204)
def delete_permission(permission_id: int, db: Session = Depends(get_db_session)):
    """
    Delete permission by ID
    """
    try:
        permission_service = PermissionService(db)
        permission_service.delete_permission(permission_id)
    except EntityDoesNotExistError as e:
        logger.error(f"Permission not found: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail="Permission not found")
    except ServiceError as e:
        logger.error(f"Service error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail='Service error')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Unexpected error')

@router.get("", tags=["Permissions"], response_model=PermissionListResponse)
def search_permissions(name: Optional[str] = None, category: Optional[str] = None, db: Session = Depends(get_db_session)):
    """
    Search permissions
    """
    try:
        permission_service = PermissionService(db)
        return permission_service.search_permissions(name, category)
    except EntityDoesNotExistError as e:
        logger.error(f"No permissions found: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail="No permissions found matching the criteria")
    except ServiceError as e:
        logger.error(f"Service error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail='Service error')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Unexpected error')