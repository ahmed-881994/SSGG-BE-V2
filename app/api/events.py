from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pymysql import MySQLError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_user_in_token
from app.core.exceptions import EntityDoesNotExistError, ServiceError
from app.schemas.common_schema import SuccessResponse
from app.schemas.event_schema import (EventCreate, EventResponse,
                                      SearchEventsResponse)
from app.service.events.geteventattenadance import get_event_attendance_db
from app.service.events.updateevent import update_event_db
from app.service.events.updateeventattendance import update_event_attendance_db
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["Events"], dependencies=[Depends(get_user_in_token)])


@router.get("", response_model=SearchEventsResponse)
def search_events(entityID: Optional[int] = None, startDate: Optional[str] = None, endDate: Optional[str] = None, name: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Search events by (Name, Team, Start and End dates)
    """
    try:
        event_service = EventService(db)
        return event_service.search_events(name=name, start_date=startDate, end_date=endDate, entity_id=entityID)
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("" , status_code=201, response_model=EventResponse)
def create_event(body: EventCreate, db: Session = Depends(get_db), current_user = Depends(get_user_in_token)):
    """
    Creates a new event
    """
    try:
        event_service = EventService(db)
        return event_service.create_event(body.model_dump(), current_user_id=current_user.id)
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """
    Gets event by ID
    """
    try:
        event_service = EventService(db)
        return event_service.get_event_by_event_id(event_id)
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.patch("/{event_id}", response_model=SuccessResponse, responses={
    200: {"description": "Success", "model": SuccessResponse}})
def update_event(event_id: int, body: dict):
    """
    Updates event by ID
    """
    try:
        return update_event_db(event_id, body)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )

@router.get("/{event_id}/attendance", response_model=dict, responses={
    200: {"description": "Success", "model": dict}})
def get_event_attendance(event_id: int):
    """
    Gets the attendance list of an event
    """
    try:
        return get_event_attendance_db(event_id)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )

@router.patch("/{event_id}/attendance", response_model=SuccessResponse, responses={
    200: {"description": "Success", "model": SuccessResponse}})
def update_event_attendance(event_id: int, body: dict):
    """
    Updates members attendance in an event
    """
    try:
        return update_event_attendance_db(event_id, body)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )