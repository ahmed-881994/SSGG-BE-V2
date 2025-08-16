from typing import List, Optional

from fastapi import APIRouter, Depends
from pymysql import MySQLError

from app.core.exceptions import ServiceError
from app.core.logging_middleware import logger
from app.schema.members.member import (MemberAddUpdate, MemberAttendance,
                                       MemberGet)
from app.service.auth.dependencies import get_active_user
from app.service.members.addmember import add_member_db
from app.service.members.getmember import get_member_db
from app.service.members.getmemberattendance import get_member_attendance_db
from app.service.members.searchmembers import search_members_db
from app.service.members.updatemember import update_member_db

router = APIRouter(prefix="/members", tags=["Members"], dependencies=[Depends(get_active_user)])


@router.get("", tags=["Members"], response_model=List[MemberGet], responses={
    200: {"description": "Success", "model": List[MemberGet]}})
def search_members(name: Optional[str] = None, teamID: Optional[int] = None):
    """
    Search members by (Name, Team)
    """
    try:
        return search_members_db(name, teamID)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )


@router.post("", status_code=201, responses={
    201: {"description": "Member created successfully", "model": MemberAddUpdate}})
def add_member(body: MemberAddUpdate):
    """
    Creates a new member
    """
    try:
        return add_member_db(body)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )


@router.get("/{member_id}", response_model=MemberGet, responses={
    200: {"description": "Success", "model": MemberGet}}, response_model_exclude_none=True)
def get_member(member_id: str):
    """
    Get Member by ID
    """
    try:
        return get_member_db(member_id)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        logger.error(f"Error fetching member {member_id}: {error.args}")
        raise ServiceError(message=error.args[1], name="Database Error" )


@router.patch("/{member_id}", responses={
    200: {"description": "Member updated successfully", "model": MemberAddUpdate}})
def update_member(member_id: str, body: MemberAddUpdate):
    """
    Updates a member
    """
    try:
        return update_member_db(member_id, body)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )


@router.get("/{member_id}/attendance", responses={
    200: {"description": "Success", "model": MemberAttendance}})
def get_member_attendance(member_id: str):
    """
    Gets member attendance by ID
    """
    try:
        return get_member_attendance_db(member_id)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )
