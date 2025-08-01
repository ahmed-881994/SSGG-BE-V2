from typing import Dict, List

from fastapi import APIRouter
from fastapi.params import Depends
from pymysql import MySQLError

from app.exceptions.exceptions import ServiceError
from app.schema.common import SuccessResponse
from app.schema.entities.add_entity_member import AddEntityMemberRequest
from app.schema.entities.create_entity import CreateEntityRequest
from app.service.auth.users import login_user
from app.service.entities.add_entity_member import add_entity_member_db
from app.service.entities.create_entity import create_entity_db

router = APIRouter(prefix="/entities", tags=["Entities"], dependencies=[Depends(login_user)])

@router.get("/{entityType}/{entityID}", tags=["Entities"])
def get_entity_details(entityType: str, entityID: int):
    """
    Get details for a specific entity type and ID.
    
    Args:
        entityType (int): The type of the entity (1.Team, 2.Stage, 3.AgeGroup, 4.GenderGroup).
        entityID (int): The ID of the entity.
    
    Returns:
        dict: A dictionary containing the details of the entity.
    """
    # Placeholder for actual implementation
    # return get_entity_details_db(entityType, entityID)

@router.post("", tags=["Entities"], responses={
    200: {"description": "Success", "model": SuccessResponse}})
def create_entity(body: CreateEntityRequest):
    """
    Create a new entity.
    
    Args:
        entityType (int): The type of the entity (1.Team, 2.Stage, 3.AgeGroup, 4.GenderGroup).
        entityID (int): The ID of the entity.
        managerID (int): The ID of the manager to assign.
    
    Returns:
        dict: A confirmation message or details about the assignment.
    """
    try:
        return create_entity_db(body)
    except MySQLError as error:
        raise ServiceError(message=error.args[1], name="Database Error" )

@router.post("/{entityID}/members", tags=["Entities"], responses={
    200: {"description": "Success", "model": SuccessResponse}})
def add_entity_members(body: List[AddEntityMemberRequest], entityID: int):
    """
    Add a member to an entity.
    
    Args:
        body (List[AddEntityMemberRequest]): The request body containing member details.
    
    Returns:
        dict: A confirmation message or details about the added member.
    """
    try:
        return add_entity_member_db(body, entityID)
    except MySQLError as error:
        raise ServiceError(message=error.args[1], name="Database Error" )