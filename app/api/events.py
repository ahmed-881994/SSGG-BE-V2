

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pymysql import MySQLError

from app.schema.auth.user import User
from app.schema.common import SuccessResponse
from app.schema.events.events import Event, EventAttendance, EventCreate, UpdateEventAttendance
from app.service.auth.users import get_current_active_user
from app.service.events.createevent import create_event_db
from app.service.events.getevent import get_event_db
from app.service.events.geteventattenadance import get_event_attendance_db
from app.service.events.searchevents import search_events_db
from app.service.events.updateevent import update_event_db
from app.service.events.updateeventattendance import update_event_attendance_db


router = APIRouter(prefix="/events", tags=["Events"], dependencies=[Depends(get_current_active_user)])


@router.get("", response_model=List[Event], responses={
    200: {"description": "Success", "model": List[Event]}})
def search_events(teamID: Optional[int] = None, startDate: Optional[str] = None, endDate: Optional[str] = None, name: Optional[str] = None):
    """
    Search events by (Name, Team, Start and End dates)
    """
    try:
        return search_events_db(teamID, startDate, endDate, name)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)

@router.post("" , status_code=201, response_model=SuccessResponse, responses={
    200: {"description": "Success", "model": SuccessResponse}})
def create_event(body: EventCreate):
    """
    Creates a new event
    """
    try:
        return create_event_db(body)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)

@router.get("/{event_id}", response_model=Event, responses={
    200: {"description": "Success", "model": Event}})
def get_event(event_id: int):
    """
    Gets event by ID
    """
    try:
        return get_event_db(event_id)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)


@router.patch("/{event_id}", response_model=SuccessResponse, responses={
    200: {"description": "Success", "model": SuccessResponse}})
def update_event(event_id: int, body: EventCreate):
    """
    Updates event by ID
    """
    try:
        return update_event_db(event_id, body)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)

@router.get("/{event_id}/attendance", response_model=EventAttendance, responses={
    200: {"description": "Success", "model": EventAttendance}})
def get_event_attendance(event_id: int):
    """
    Gets the attendance list of an event
    """
    try:
        return get_event_attendance_db(event_id)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)

@router.patch("/{event_id}/attendance", response_model=SuccessResponse, responses={
    200: {"description": "Success", "model": SuccessResponse}})
def update_event_attendance(event_id: int, body: UpdateEventAttendance):
    """
    Updates members attendance in an event
    """
    try:
        return update_event_attendance_db(event_id, body)
    except MySQLError as error:
        raise HTTPException(status_code=500, detail=error.args)