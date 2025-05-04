from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.service.addmember import add_member_db
from app.service.getmember import format_member_record, get_member_db
from app.service.getmemberattendance import format_member_attendance_records, get_member_attendance_db
from app.service.searchmembers import format_member_records, search_members_db
from app.service.updatemember import update_member_db

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
    This endpoint is used to check if the FastAPI application is running.

    Returns:
        Dict: A dictionary with a welcome message.
        - message (str): A welcome message indicating the application is running.
    """
    return {"message": "Welcome to the FastAPI application!"}


@app.get("/members", tags=["Members"])
def search_members(name: str | None = None, teamID: int | None = None):
    """
    Search members by (Name, Team)
    """
    records = search_members_db(name, teamID)
    if records:
        data = format_member_records(records)
        return data
    else:
        raise HTTPException(
            status_code=404, detail="No members found with the provided criteria.",)


@app.post("/members", tags=["Members"])
def add_member(body: dict):
    """
    Creates a new member
    """
    return add_member_db(body)


@app.get("/members/{member_id}", tags=["Members"])
def get_member(member_id: str):
    """
    Get Member by ID
    """
    records = get_member_db(member_id)
    if records:
        data = format_member_record(records)
        return data
    else:
        raise HTTPException(
            status_code=404, detail="No members found with the provided criteria.",)


@app.patch("/members/{member_id}", tags=["Members"])
def update_member(member_id: str, body: dict):
    """
    Updates a member
    """
    result = update_member_db(member_id, body)

    if result == 0:
        return {"message": "Member updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Member not found")


@app.get("/members/{member_id}/attendance", tags=["Members"], operation_id="getMemberAttendance")
def get_member_attendance(member_id: str):
    """
    Gets member attendance by ID
    """
    result = get_member_attendance_db(member_id)

    if result is not None:
        if result[0] == 0:
            records = result[1]
            return format_member_attendance_records(records)
        elif result[0] == -1:
            raise HTTPException(status_code=404, detail="Member not found.")
        elif result[0] == -2:
            raise HTTPException(
                status_code=404, detail="No attendance records found for the provided member ID.")


@app.get("/teams", tags=["Teams"], operation_id="getTeams")
def get_teams(team_name: str | None = None, stage_id: int | None = None, leader_id: str | None = None):
    """
    Search teams by (Team Name, LeaderID, StageID)
    """
    pass


@app.post("/teams/transfer", tags=["Teams"], operation_id="transferTeam")
def transfer_team(body: dict):
    """
    Transfer a member to another team
    """
    pass


@app.get("/teams/{team_id}/members", tags=["Teams"], operation_id="getTeamMembers")
def get_team_members(team_id: str):
    """
    Get all members in a team
    """
    pass


@app.get("/teams/{team_id}/attendance", tags=["Teams"], operation_id="getTeamAttendance")
def get_team_attendance(team_id: str):
    """
    Get all attendance records for a team
    """
    pass


@app.post("/teams/{team_id}/attendance", tags=["Teams"], operation_id="takeTeamAttendance")
def take_team_attendance(team_id: str):
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
        content={"message": exc.detail},
    )

# @app.exception_handler(ValidationError)
# async def validation_exception_handler(request, exc):
#     """
#     Custom exception handler for ValidationError.
#     This function handles validation errors and returns a JSON response with the error details.

#     Args:
#         request: The HTTP request object.
#         exc: The ValidationError object.

#     Returns:
#         JSONResponse: A JSON response containing the error details.
#     """
#     return JSONResponse(
#         status_code=422,
#         content={"message": "Validation error", "errors": exc.errors()},
#     )
