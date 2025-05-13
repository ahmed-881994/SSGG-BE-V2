from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pymysql import MySQLError

from app.exceptions.exceptions import ServiceError
from app.schema.common import SuccessResponse
from app.schema.teams.teams import Team, TeamAdd, TeamAttendance, TeamTransfer
from app.service.teams.addteammember import add_team_member_db
from app.service.teams.getteamattendance import get_team_attendance_db
from app.service.teams.getteammembers import get_team_members_db
from app.service.teams.searchteams import search_teams_db
from app.service.teams.transferteammembers import transfer_team_members_db

router = APIRouter(prefix="/teams", tags=["Teams"], dependencies=[Depends(get_current_active_user)])


@router.get("", tags=["Teams"], response_model=List[Team], responses={
    200: {"description": "Success", "model": List[Team]}})
def get_teams(teamName: Optional[str] = None, stageID: Optional[int] = None, leaderID: Optional[str] = None):
    """
    Search teams by (Team Name, LeaderID, StageID)
    """
    try:
        return search_teams_db(teamName, stageID, leaderID)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )


@router.post("/transfer", tags=["Teams"], response_model= SuccessResponse, responses={
    200: {"description": "Success", "model": SuccessResponse}})
def transfer_team(body: List[TeamTransfer]):
    """
    Transfer a list of members to a team
    """
    try:
        return transfer_team_members_db(body)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )


@router.get("/{team_id}/members", tags=["Teams"], response_model= Team, responses={
    200: {"description": "Success", "model": Team}})
def get_team_members(team_id: int):
    """
    Get all members in a team
    """
    try:
        return get_team_members_db(team_id)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )


@router.post("/{teamID}/members", tags=["Teams"], response_model= SuccessResponse, responses={
    200: {"description": "Success", "model": SuccessResponse}})
def add_team_members(teamID: int, body: List[TeamAdd]):
    """
    Adds a list of members to a team
    """
    try:
        return add_team_member_db(teamID ,body)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )


@router.get("/{team_id}/attendance", tags=["Teams"], response_model= List[TeamAttendance], responses={
    200: {"description": "Success", "model": List[TeamAttendance]}})
def get_team_attendance(team_id: int):
    """
    Get all attendance records for a team
    """
    try:
        return get_team_attendance_db(team_id)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )
