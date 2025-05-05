from typing import Dict, Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymysql import MySQLError

from app.service.members.addmember import add_member_db
from app.service.members.getmember import get_member_db
from app.service.members.getmemberattendance import get_member_attendance_db
from app.service.members.searchmembers import search_members_db
from app.service.members.updatemember import update_member_db
from app.service.teams.getteamattendance import get_team_attendance_db
from app.service.teams.getteammembers import get_team_members_db
from app.service.teams.searchteams import search_teams_db
from app.service.teams.transferteammembers import transfer_team_members_db

app = FastAPI()

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
    return {"message": "Welcome to the SSGG-V2 apAPIpAPIlication!"}

#------------------------------#
# Members Endpoints
#------------------------------#

@app.get("/members", tags=["Members"])
def search_members(name: Optional[str] = None, teamID: Optional[int] = None):
    """
    Search members by (Name, Team)
    """
    try:
        return search_members_db(name, teamID)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)
    # if records:
    #     data = format_member_records(records)
    #     return data
    # else:
    #     raise HTTPException(
    #         status_code=404, detail="No members found with the provided criteria.")


@app.post("/members", tags=["Members"])
def add_member(body: Dict):
    """
    Creates a new member
    """
    try:
        return add_member_db(body)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)


@app.get("/members/{member_id}", tags=["Members"])
def get_member(member_id: str):
    """
    Get Member by ID
    """
    try:
        return get_member_db(member_id)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)


@app.patch("/members/{member_id}", tags=["Members"])
def update_member(member_id: str, body: Dict):
    """
    Updates a member
    """
    try:
        return update_member_db(member_id, body)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)


@app.get("/members/{member_id}/attendance", tags=["Members"], operation_id="getMemberAttendance")
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

@app.get("/teams", tags=["Teams"], operation_id="getTeams")
def get_teams(team_name: Optional[str] = None, stage_id: Optional[int] = None, leader_id: Optional[str] = None):
    """
    Search teams by (Team Name, LeaderID, StageID)
    """
    try:
        return search_teams_db(team_name, stage_id, leader_id)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)


@app.post("/teams/transfer", tags=["Teams"], operation_id="transferTeam")
def transfer_team(body: List[Dict]):
    """
    Transfer a list of members to a team
    """
    try:
        return transfer_team_members_db(body)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)


@app.get("/teams/{team_id}/members", tags=["Teams"], operation_id="getTeamMembers")
def get_team_members(team_id: int):
    """
    Get all members in a team
    """
    try:
        return get_team_members_db(team_id)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)


@app.get("/teams/{team_id}/attendance", tags=["Teams"], operation_id="getTeamAttendance")
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

@app.get("/events", tags=["Events"], operation_id="searchEvents")
def search_events(team_id: Optional[int] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, event_name: Optional[str] = None):
    """
    Search events by (Name, Team, Start and End dates)
    """
    pass

@app.post("/events/{event_id}/attendance", tags=["Events"], operation_id="takeEventAttendance")
def take_team_attendance(team_id: int):
    """
    Get all members in a team
    """
    pass


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Custom exception handler for HTTPException.
    This function handles HTTP exceptions and returns a JSON response with the error details.

    Args:
        request: The HTTP request object.
        exc: The HTTPException object.

    Returns:
        JSONResponse: A JSON response containing the error details.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
