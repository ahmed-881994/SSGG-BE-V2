from typing import Optional

from fastapi import APIRouter, Depends
from pymysql import MySQLError

from app.exceptions.exceptions import ServiceError
from app.schema.common import SuccessResponse
from app.schema.users.create_user import CreateUserRequest
from app.schema.users.search_users import SearchUsersResponse
from app.schema.users.user import User
from app.service.auth.dependencies import get_active_user
from app.service.users.create_user import create_user_db
from app.service.users.search_users import search_users_db

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(get_active_user)])

@router.get("", response_model=SearchUsersResponse, responses={200: {"description": "Success", "model": SearchUsersResponse}})
def search_users(userName: Optional[str]= None, userID: Optional[str]= None):
    """Search for users by Name or ID.
    Note: Not sending any of the criteria returns all users.
    """
    try:
        return search_users_db(user_name=userName, user_id=userID)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )

@router.post("", responses={200: {"description": "Success", "model": SuccessResponse}})
def create_user(user: CreateUserRequest):
    """Create a new user."""
    try:
        return create_user_db(user=user)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )    

@router.patch("/{user_id}")
def update_user(user_id: int, user: dict):
    """Update an existing user."""
    try:
        return update_user_db(user=user)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )   

@router.delete("/{user_id}")
def delete_user(user_id: int):
    """Delete an existing user."""
    try:
        return delete_user_db(user_id=user_id)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )   
@router.get("/{user_id}")
def get_user(user_id: int):
    """Get details of an existing user."""
    try:
        return get_user_db(user_id=user_id)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )   