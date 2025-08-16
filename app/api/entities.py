from typing import List, Optional

from fastapi import APIRouter
from fastapi.params import Depends
from pymysql import MySQLError

from app.core.exceptions import ServiceError
from app.schema.common import EntityMember, SuccessResponse
from app.schema.entities.add_entity_member import AddEntityMemberRequest
from app.schema.entities.create_entity import CreateEntityRequest
from app.schema.entities.search_entities import SearchEntitiesResponse
from app.schema.entities.transfer_entity_members import EntityTransfer
from app.schema.entities.update_entity_member_role import \
    UpdateEntityMemberRoleRequest
from app.service.auth.dependencies import get_active_user
from app.service.entities.add_entity_member import add_entity_member_db
from app.service.entities.create_entity import create_entity_db
from app.service.entities.get_entity_members import get_entity_members_db
from app.service.entities.search_entities import search_entities_db
from app.service.entities.transfer_entity_members import \
    transfer_entity_members_db
from app.service.entities.update_entity_member_role import \
    update_entity_member_role_db

router = APIRouter(prefix="/entities",
                   tags=["Entities"], dependencies=[Depends(get_active_user)])


@router.get("", tags=["Entities"], response_model=List[SearchEntitiesResponse], responses={
    200: {"description": "Success", "model": List[SearchEntitiesResponse]}})
def search_entities(entityID: Optional[int] = None, entityParentID: Optional[int] = None, entityName: Optional[str] = None):
    """ 
    Search entities by ID, Parent ID, and Name.
    Args:
        entityID (Optional[int]): The ID of the entity.
        entityParentID (Optional[int]): The Parent ID of the entity.
        entityName (Optional[str]): The Name of the entity.
    """
    try:
        return search_entities_db(entityID, entityParentID, entityName)
    except MySQLError as error:
        raise ServiceError(message=error.args[1], name="Database Error")


@router.post("", tags=["Entities"], responses={
    200: {"description": "Success", "model": SuccessResponse}})
def create_entity(body: CreateEntityRequest):
    """
    Create a new entity.
    """
    try:
        return create_entity_db(body)
    except MySQLError as error:
        raise ServiceError(message=error.args[1], name="Database Error")


@router.post("/transfer", tags=["Entities"], response_model=SuccessResponse, responses={
    200: {"description": "Success", "model": SuccessResponse}})
def transfer_entity(body: List[EntityTransfer]):
    """
    Transfer a list of members to an entity
    """
    try:
        return transfer_entity_members_db(body)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error")


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
        raise ServiceError(message=error.args[1], name="Database Error")


@router.get("/{entityID}/members", tags=['Entities'], response_model=list[EntityMember], responses={
    200: {"description": "Success", "model": list[EntityMember]}})
def get_entity_members(entityID: int):
    """
    Get members of an entity.
    """
    try:
        return get_entity_members_db(entityID)
    except MySQLError as error:
        raise ServiceError(message=error.args[1], name="Database Error")
    
@router.post("/{entityID}/members/roles", tags=['Entities'], response_model=SuccessResponse, responses={
    200: {"description": "Success", "model": SuccessResponse}})
def update_entity_member_role(entityID: int, body: UpdateEntityMemberRoleRequest):
    """ Update roles of members in an entity.
    """
    try:
        return update_entity_member_role_db(entityID, body)
    except MySQLError as error:
        raise ServiceError(message=error.args[1], name="Database Error")