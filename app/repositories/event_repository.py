from datetime import datetime
from logging import getLogger
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import ServiceError
from app.models.attendance_model import Attendance
from app.models.attendance_state_model import AttendanceState
from app.models.entity_model import Entity
from app.models.event_model import Event
from app.repositories.base_repository import BaseRepository

logger = getLogger(__name__)

class EventRepository(BaseRepository[Event]):
    """Repository for Event database operations."""

    def __init__(self, db_session: Session):
        super().__init__(db_session, Event)
        
    
    def get_next_event_id(self) -> int:
        """Get the next available event ID."""
        try:
            return (self.db.query(func.max(Event.event_id)).scalar() or 0) + 1
        except SQLAlchemyError as e:
            raise ServiceError(
                message=f"Failed to retrieve next event ID: {str(e)}",
                name="Database Error"
            )


    def get_event_by_event_id(self, event_id: int) -> Event | None:
        """Get an event by its ID."""
        try:
            return self.db.query(Event).filter(Event.id == event_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching event by ID {event_id}: {e}")
            raise ServiceError(message=f"Failed to retrieve event: {str(e)}",
                name="Database Error")

    def search_events(self, name: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, entity_id: Optional[int] = None) -> list[Event]:
        """Search for events based on various criteria."""
        try:
            query = self.db.query(Event)
            if name:
                query = query.filter(or_(Event.event_name_en.ilike(f"%{name}%"), Event.event_name_ar.ilike(f"%{name}%")))
            if start_date:
                query = query.filter(Event.event_start_date >= start_date)
            if end_date:
                query = query.filter(Event.event_end_date <= end_date)
            if entity_id is not None:
                query = query.filter(
                    or_(
                        Event.organizing_entity_id == entity_id,
                        Event.participating_entities.any(Entity.entity_id == entity_id)
                    )
                )
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error searching events: {e}")
            raise ServiceError(message=f"Failed to search events: {str(e)}",
                               name="Database Error")


    def create_event(self, event: dict, current_user_id: int) -> Event:
        """Create a new event."""
        try:
            new_event = Event()
            new_event.event_id = self.get_next_event_id()
            new_event.event_name_en = event["event_name"]["en"]
            new_event.event_name_ar = event["event_name"]["ar"]
            new_event.event_start_date = event["event_start_date"]
            new_event.event_end_date = event["event_end_date"]
            new_event.event_location = event["event_location"]
            new_event.is_multi_team = event["is_multi_team"]
            new_event.event_type_id = event["event_type_id"]
            new_event.organizing_entity_id = event["organizing_entity_id"]
            new_event.created_at = datetime.now().date()
            new_event.created_by = current_user_id

            super().create(new_event)
            
            # Get the "Not Specified" attendance state ID from the database
            not_specified_state = self.db.query(AttendanceState).filter(
                AttendanceState.attendance_state_name_en == "Not Specified"
            ).first()
            
            if not_specified_state is None:
                raise ServiceError(
                    message="Default attendance state 'Not Specified' not found in database",
                    name="Configuration Error"
                )

            organizing_entity_members = self.db.query(Entity).filter(Entity.entity_id == event["organizing_entity_id"]).first().members

            for member in organizing_entity_members:
                member_attendance = Attendance()
                member_attendance.event_id = new_event.event_id
                member_attendance.member_id = member.member_id
                member_attendance.attendance_state_id = not_specified_state.attendance_state_id
                new_event.attendance_records.append(member_attendance)

            if event.get("is_multi_team") and event.get("participating_entities_ids"):
                for entity_id in event["participating_entities_ids"]:
                    participating_entity_members = self.db.query(Entity).filter(Entity.entity_id == entity_id).first().members
                    for member in participating_entity_members:
                        if member not in organizing_entity_members:
                            member_attendance = Attendance()
                            member_attendance.event_id = new_event.event_id
                            member_attendance.member_id = member.member_id
                            member_attendance.attendance_state_id = not_specified_state.attendance_state_id
                            new_event.attendance_records.append(member_attendance)
                            
            self.db.commit()

            return new_event
        except SQLAlchemyError as e:
            logger.error(f"Error creating event: {e}")
            raise ServiceError(message=f"Failed to create event: {str(e)}",
                               name="Database Error")