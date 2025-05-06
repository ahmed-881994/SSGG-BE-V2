from typing import Dict, Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from pymysql import MySQLError

from app.schema.common import ErrorResponse
from app.schema.members.member import MemberAddUpdate, MemberAttendance, MemberGet
from app.service.events.createevent import create_event_db
from app.service.events.getevent import get_event_db
from app.service.events.geteventattenadance import get_event_attendance_db
from app.service.events.searchevents import search_events_db
from app.service.events.updateevent import update_event_db
from app.service.events.updateeventattendance import update_event_attendance_db
from app.service.members.addmember import add_member_db
from app.service.members.getmember import get_member_db
from app.service.members.getmemberattendance import get_member_attendance_db
from app.service.members.searchmembers import search_members_db
from app.service.members.updatemember import update_member_db
from app.service.teams.getteamattendance import get_team_attendance_db
from app.service.teams.getteammembers import get_team_members_db
from app.service.teams.searchteams import search_teams_db
from app.service.teams.transferteammembers import transfer_team_members_db

app = FastAPI(version="2.0.0", responses={
    500: {"description": "Internal server error", "model": ErrorResponse},
})

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # required
    allow_credentials=True,           # allow cookies/credentials
    # or ["*"] :contentReference[oaicite:1]{index=1}
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    # or e.g. ["Authorization","Content-Type"] :contentReference[oaicite:2]{index=2}
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def read_root():
    """Health check endpoint.
    This endpoint is used to check if the SSGG-V2 application is running.

    Returns:
        Dict: A dictionary with a welcome message.
        - message (str): A welcome message indicating the application is running.
    """
    return {"message": "Welcome to the SSGG-V2 API!"}

#------------------------------#
# Members Endpoints
#------------------------------#

@app.get("/members", tags=["Members"], responses={
    200: {"description": "Success", "model": List[MemberGet]}})
def search_members(name: Optional[str] = None, teamID: Optional[int] = None):
    """
    Search members by (Name, Team)
    """
    try:
        return search_members_db(name, teamID)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)

@app.post("/members", tags=["Members"], status_code=201, responses={
    201: {"description": "Member created successfully", "model": MemberAddUpdate}})
def add_member(body: MemberAddUpdate):
    """
    Creates a new member
    """
    try:
        return add_member_db(body)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)


@app.get("/members/{member_id}", tags=["Members"], responses={
    200: {"description": "Success", "model": MemberGet}})
def get_member(member_id: str):
    """
    Get Member by ID
    """
    try:
        return get_member_db(member_id)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)


@app.patch("/members/{member_id}", tags=["Members"], responses={
    200: {"description": "Member updated successfully", "model": MemberAddUpdate}})
def update_member(member_id: str, body: MemberAddUpdate):
    """
    Updates a member
    """
    try:
        return update_member_db(member_id, body)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)


@app.get("/members/{member_id}/attendance", tags=["Members"], responses={
    200: {"description": "Success", "model": MemberAttendance}})
def get_member_attendance(member_id: str):
    """
    Gets member attendance by ID
    """
    try:
        return get_member_attendance_db(member_id)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)

#------------------------------#
# Teams Endpoints
#------------------------------#

@app.get("/teams", tags=["Teams"])
def get_teams(teamName: Optional[str] = None, stageID: Optional[int] = None, leaderID: Optional[str] = None):
    """
    Search teams by (Team Name, LeaderID, StageID)
    """
    try:
        return search_teams_db(teamName, stageID, leaderID)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)


@app.post("/teams/transfer", tags=["Teams"])
def transfer_team(body: List[Dict]):
    """
    Transfer a list of members to a team
    """
    try:
        return transfer_team_members_db(body)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)


@app.get("/teams/{team_id}/members", tags=["Teams"])
def get_team_members(team_id: int):
    """
    Get all members in a team
    """
    try:
        return get_team_members_db(team_id)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)


@app.get("/teams/{team_id}/attendance", tags=["Teams"])
def get_team_attendance(team_id: int):
    """
    Get all attendance records for a team
    """
    try:
        return get_team_attendance_db(team_id)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)

#------------------------------#
# Events Endpoints
#------------------------------#

@app.get("/events", tags=["Events"])
def search_events(teamID: Optional[int] = None, startDate: Optional[str] = None, endDate: Optional[str] = None, name: Optional[str] = None):
    """
    Search events by (Name, Team, Start and End dates)
    """
    try:
        return search_events_db(teamID, startDate, endDate, name)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)

@app.post("/events", tags=["Events"] , status_code=201)
def create_event(body: Dict):
    """
    Creates a new event
    """
    try:
        return create_event_db(body)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)

@app.get("/events/{event_id}", tags=["Events"])
def get_event(event_id: int):
    """
    Gets event by ID
    """
    try:
        return get_event_db(event_id)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)


@app.patch("/events/{event_id}", tags=["Events"])
def update_event(event_id: int, body: dict):
    """
    Updates event by ID
    """
    try:
        return update_event_db(event_id, body)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)

@app.get("/events/{event_id}/attendance", tags=["Events"], status_code=201)
def get_event_attendance(event_id: int):
    """
    Gets the attendance list of an event
    """
    try:
        return get_event_attendance_db(event_id)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)

@app.patch("/events/{event_id}/attendance", tags=["Events"])
def update_event_attendance(event_id: int, body: dict):
    """
    Updates members attendance in an event
    """
    try:
        return update_event_attendance_db(event_id, body)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)


# @app.exception_handler(HTTPException)
# async def http_exception_handler(request, exc):
#     """
#     Custom exception handler for HTTPException.
#     This function handles HTTP exceptions and returns a JSON response with the error details.

#     Args:
#         request: The HTTP request object.
#         exc: The HTTPException object.

#     Returns:
#         JSONResponse: A JSON response containing the error details.
#     """
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.detail},
#     )