from typing import Dict

from fastapi import APIRouter
from fastapi.params import Depends

from app.schema.common import SuccessResponse
from app.schema.entities.create_entity import CreateEntityRequest
from app.service.auth.users import get_current_active_user

router = APIRouter(prefix="/entities", tags=["Entities"], dependencies=[Depends(get_current_active_user)])

@router.get("/{entityType}/{entityID}", tags=["Entities"])
def get_entity_details(entityType: str, entityID: int):
    """
    Get details for a specific entity type and ID.
    
    Args:
        entityType (str): The type of the entity (e.g., "stage", "ageGroup").
        entityID (int): The ID of the entity.
    
    Returns:
        dict: A dictionary containing the details of the entity.
    """
    # Placeholder for actual implementation
    return get_entity_details_db(entityType, entityID)

@router.post("", tags=["Entities"], responses={
    200: {"description": "Success", "model": SuccessResponse}})
def create_entity(body: CreateEntityRequest):
    """
    Create a new entity.
    
    Args:
        entityType (str): The type of the entity (e.g., "member", "team").
        entityID (int): The ID of the entity.
        managerID (int): The ID of the manager to assign.
    
    Returns:
        dict: A confirmation message or details about the assignment.
    """
    # Placeholder for actual implementation
    return create_entity_db(body)

@router.post("/{entityType}/{entityID}/managers", tags=["Entities"], responses={
    200: {"description": "Success", "model": SuccessResponse}})
def assign_entity_manager(body: Dict):
    """
    Assign a manager to an entity.
    
    Args:
        entityType (str): The type of the entity (e.g., "member", "team").
        entityID (int): The ID of the entity.
        managerID (int): The ID of the manager to assign.
    
    Returns:
        dict: A confirmation message or details about the assignment.
    """
    # Placeholder for actual implementation
    return assign_entity_manager_db(body)