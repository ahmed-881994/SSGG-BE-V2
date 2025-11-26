from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.database import get_db_session
from app.core.dependencies import get_user_in_token
from app.core.exceptions import (EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.schemas.roles_schema import (RoleCreate, RoleResponse,
                                      RoleSearchResponse)
from app.services.role_service import RoleService

router = APIRouter(prefix="/roles", tags=["Roles"], dependencies=[Depends(get_user_in_token)])


@router.post("", tags=["Roles"], status_code=201, response_model=RoleResponse)
def create_role(role: RoleCreate, db: Session = Depends(get_db_session)):
    """
    Create a new role
    """
    try:
        role_service = RoleService(db)
        return role_service.create_role(role_data=role.model_dump())
    except EntityAlreadyExistsError as e:
        logger.error(f"Role already exists: {e.message}", exc_info=True)
        raise HTTPException(status_code=400, detail='Role already exists')
    except ServiceError as e:
        logger.error(f"Service error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail='Service error')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Unexpected error')

@router.get("", tags=["Roles"], response_model=RoleSearchResponse)
def search_roles(role_id: Optional[int] = None, role_name: Optional[str] = None, db: Session = Depends(get_db_session)):
    """
    Search roles
    """
    try:
        role_service = RoleService(db)
        return role_service.search_roles(role_id, role_name)
    except EntityDoesNotExistError as e:
        logger.error(f"No roles found matching criteria: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='No roles found matching criteria')
    except ServiceError as e:
        logger.error(f"Service error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail='Service error')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Unexpected error')

@router.get("/{role_id}", tags=["Roles"])
def get_role(role_id: int,db: Session = Depends(get_db_session)):
    """
    Get role by ID
    """
    try:
        role_service = RoleService(db)
        return role_service.get_role_by_id(role_id)
    except EntityDoesNotExistError as e:
        logger.error(f"Role not found: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='Role not found')
    except ServiceError as e:
        logger.error(f"Service error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail='Service error')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Unexpected error')

@router.put("/{role_id}", tags=["Roles"])
def update_role(role_id: int, db: Session = Depends(get_db_session)):
    """
    Update role by ID
    """
    return {"message": f"Role {role_id} updated successfully"}

@router.delete("/{role_id}", tags=["Roles"])
def delete_role(role_id: int):
    """
    Delete role by ID
    """
    return {"message": f"Role {role_id} deleted successfully"}

@router.put("/{role_id}/permissions", tags=["Roles"])
def update_role_permissions(role_id: int):
    """
    Update role permissions by role ID
    """
    return {"message": f"Role {role_id} permissions updated successfully"}

