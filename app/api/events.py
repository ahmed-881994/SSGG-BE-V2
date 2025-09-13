from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pymysql import MySQLError
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import get_user_in_token
from app.core.exceptions import EntityDoesNotExistError, ServiceError
from app.schemas.common_schema import SuccessResponse
from app.schemas.event_schema import (EventAttendanceResponse,
                                      EventAttendanceUpdate, EventCreate,
                                      EventResponse, EventUpdate,
                                      SearchEventsResponse)
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["Events"], dependencies=[Depends(get_user_in_token)])


@router.get("", response_model=SearchEventsResponse)
def search_events(entityID: Optional[int] = None, startDate: Optional[str] = None, endDate: Optional[str] = None, name: Optional[str] = None, db: Session = Depends(get_db_session)):
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
def create_event(body: EventCreate, db: Session = Depends(get_db_session), current_user = Depends(get_user_in_token)):
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
def get_event(event_id: int, db: Session = Depends(get_db_session)):
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


@router.put("/{event_id}", response_model=EventResponse)
def update_event(event_id: int, body: EventUpdate, db: Session = Depends(get_db_session), current_user = Depends(get_user_in_token)):
    """
    Updates event by ID
    """
    try:
        event_service = EventService(db)
        return event_service.update_event(event_id, body.model_dump(exclude_none=True), current_user.id)
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db_session)):
    """
    Deletes event by ID
    """
    try:
        event_service = EventService(db)
        event_service.delete_event(event_id)
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/{event_id}/attendance", response_model=EventAttendanceResponse)
def get_event_attendance(event_id: int, db: Session = Depends(get_db_session)):
    """
    Gets the attendance list of an event
    """
    try:
        event_service = EventService(db)
        return event_service.get_event_attendance(event_id)
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.put("/{event_id}/attendance", response_model=SuccessResponse)
def update_event_attendance(event_id: int, body: EventAttendanceUpdate, db: Session = Depends(get_db_session), current_user = Depends(get_user_in_token)):
    """
    Updates members attendance in an event
    """
    try:
        event_service = EventService(db)
        event_service.update_event_attendance(event_id, body.model_dump(), current_user.id)
        return {"message": "Event attendance updated successfully"}
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")