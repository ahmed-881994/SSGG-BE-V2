from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.database import get_db_session
from app.core.dependencies import get_user_in_token
from app.core.exceptions import (EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.schemas.common_schema import SuccessResponse
from app.schemas.entity_schema import (EntityAssign, EntityAttendanceResponse,
                                       EntityCreate,
                                       EntityHierarchicalResponse,
                                       EntityMembersResponse, EntityResponse,
                                       EntitySearchResponse, EntityTransfer,
                                       RoleUpdate)
from app.services.entity_service import EntityService

router = APIRouter(prefix="/entities",tags=["Entities"],
                    dependencies=[Depends(get_user_in_token)])


@router.get("",  response_model=EntitySearchResponse)
def search_entities(entityID: Optional[int] = None, entityParentID: Optional[int] = None, entityName: Optional[str] = None, entityTypeID: Optional[int] = None, db: Session = Depends(get_db_session)):
    """ 
    Search entities by ID, Parent ID, and Name.
    Args:
        entityID (Optional[int]): The ID of the entity.
        entityParentID (Optional[int]): The Parent ID of the entity.
        entityName (Optional[str]): The Name of the entity.
        entityType (Optional[int]): The Type of the entity.
    """
    try:
        entity_service = EntityService(db)
        return entity_service.search_entities(entity_id=entityID, entity_parent_id=entityParentID, entity_name=entityName, entity_type_id=entityTypeID)
    except EntityDoesNotExistError as e:
        logger.error(f"Entity not found during search: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='Entity not found')
    except ServiceError as e:
        logger.error(f"Database error during entity search: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Unexpected error during entity search: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected error")


@router.post("",  response_model=EntityResponse, status_code=201)
def create_entity(body: EntityCreate, db: Session = Depends(get_db_session)):
    """
    Create a new entity.
    """
    try:
        entity_service = EntityService(db)
        return entity_service.create_entity(entity_data=body.model_dump())
    except EntityDoesNotExistError as e:
        logger.error(f"Entity not found during creation: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='Entity not found')
    except EntityAlreadyExistsError as e:
        logger.error(f"Entity already exists during creation: {e.message}", exc_info=True)
        raise HTTPException(status_code=409, detail='Entity already exists')
    except ServiceError as e:
        logger.error(f"Database error during entity creation: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Unexpected error during entity creation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected error")


@router.post("/transfer",  response_model=SuccessResponse, responses={
    200: {"description": "Success", "model": SuccessResponse}})
def transfer_entity(body: List[EntityTransfer], db: Session = Depends(get_db_session)):
    """
    Transfer a list of members to an entity
    """
    
    try:
        entity_service = EntityService(db)
        if entity_service.transfer_entity_members(entity_transfer_data=body):
            return SuccessResponse(message="Members transferred successfully.")
    except EntityDoesNotExistError as e:
        logger.error(f"Entity not found during transfer: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='Entity not found')
    except ServiceError as e:
        logger.error(f"Database error during entity transfer: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Unexpected error during entity transfer: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected error")

@router.post("/{entityID}/members", response_model=SuccessResponse, responses={
    200: {"description": "Success", "model": SuccessResponse}})
def add_entity_members(body: EntityAssign, entityID: int, db: Session = Depends(get_db_session)):
    """
    Add a member to an entity.

    Args:
        body (List[dict]): The request body containing member details.

    Returns:
        dict: A confirmation message or details about the added member.
    """
    try:
        entity_service = EntityService(db)
        memberships_data = [membership.model_dump() for membership in body.memberships]
        if entity_service.assign_member_to_entity(memberships=memberships_data, entity_id=entityID):
            return {"message": "Members added successfully"}
    except EntityDoesNotExistError as e:
        logger.error(f"Entity not found during member addition: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='Entity not found')
    except ServiceError as e:
        logger.error(f"Database error during member addition: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Unexpected error during member addition: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected error")
@router.get("/{entityID}", tags=['Entities'], response_model=EntityHierarchicalResponse)
def get_entity(entityID: int, db: Session = Depends(get_db_session)):
    try:
        entity_service = EntityService(db)
        return entity_service.get_entity(entity_id=entityID)
    except EntityDoesNotExistError as e:
        logger.error(f"Entity not found during retrieval: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='Entity not found')
    except ServiceError as e:
        logger.error(f"Database error during entity retrieval: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Unexpected error during entity retrieval: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected error")
    
@router.put("/{entityID}", tags=['Entities'], response_model=EntityResponse)
def update_entity(entityID: int, body: EntityCreate, db: Session = Depends(get_db_session)):
    try:
        entity_service = EntityService(db)
        return entity_service.update_entity(entity_id=entityID, entity_data=body.model_dump())
    except EntityDoesNotExistError as e:
        logger.error(f"Entity not found during update: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='Entity not found')
    except ServiceError as e:
        logger.error(f"Database error during update: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Unexpected error during update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected error")
@router.delete("/{entityID}", status_code=204, tags=['Entities'])
def delete_entity(entityID: int, db: Session = Depends(get_db_session)):
    try:
        entity_service = EntityService(db)
        entity_service.delete_entity(entity_id=entityID)
    except EntityDoesNotExistError as e:
        logger.error(f"Entity not found during deletion: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='Entity not found')
    except ServiceError as e:
        logger.error(f"Database error during deletion: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Unexpected error during deletion: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected error")
@router.get("/{entityID}/members", tags=['Entities'], response_model=EntityMembersResponse)
def get_entity_members(entityID: int, includeInactive: Optional[bool] = False, roleId: Optional[int] = None, db: Session = Depends(get_db_session)):
    """
    Get members of an entity.
    """
    try:
        entity_service = EntityService(db)
        return entity_service.get_entity_members(entity_id=entityID, include_inactive=includeInactive or False, role_id=roleId)
    except EntityDoesNotExistError as e:
        logger.error(f"Entity not found during member retrieval: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='Entity not found')
    except ServiceError as e:
        logger.error(f"Database error during member retrieval: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Unexpected error during member retrieval: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected error")
    
@router.post("/{entityID}/members/roles", tags=['Entities'], response_model=SuccessResponse, responses={
    200: {"description": "Success", "model": SuccessResponse}})
def update_entity_member_role(entityID: int, body: RoleUpdate, db: Session = Depends(get_db_session)):
    """ Update roles of members in an entity.
    """
    try:
        entity_service = EntityService(db)
        if entity_service.update_entity_member_role(entity_id=entityID, body=body.model_dump()):
            return {"message": "Roles updated successfully"}
    except EntityDoesNotExistError as e:
        logger.error(f"Entity not found during role update: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='Entity not found')
    except ServiceError as e:
        logger.error(f"Database error during role update: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Unexpected error during role update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected error")
    
@router.get("/{entityID}/attendance", tags=['Entities'], response_model=EntityAttendanceResponse)
def get_entity_attendance(entityID: int, db: Session = Depends(get_db_session)):
    """
    Get attendance records of entity members.
    """
    try:
        entity_service = EntityService(db)
        return entity_service.get_entity_attendance(entity_id=entityID)
    except EntityDoesNotExistError as e:
        logger.error(f"Entity not found during attendance retrieval: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='Entity not found')
    except ServiceError as e:
        logger.error(f"Database error during attendance retrieval: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Unexpected error during attendance retrieval: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected error")