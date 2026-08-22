from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.exceptions import ServiceError
from app.models.attendance_model import Attendance
from app.models.attendance_state_model import AttendanceState
from app.models.entity_member_model import EntityMember
from app.models.entity_model import Entity
from app.models.event_entity_model import EventEntity
from app.models.event_model import Event
from app.repositories.base_repository import BaseRepository
from app.repositories.entity_repository import EntityRepository
from app.util.egy_time import get_egypt_time


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
            return self.db.query(Event).filter(Event.event_id == event_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching event by ID {event_id}: {e}")
            raise ServiceError(message=f"Failed to retrieve event: {str(e)}",
                               name="Database Error")

    def search_events(self, requester_member_id: str, name: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, entity_id: Optional[int] = None, include_children: bool = False) -> list[Event]:
        """Search for events based on various criteria."""
        try:
            query = self.db.query(Event)
            if name:
                query = query.filter(or_(Event.event_name_en.ilike(
                    f"%{name}%"), Event.event_name_ar.ilike(f"%{name}%")))
            if start_date:
                query = query.filter(Event.event_start_date >= start_date)
            if end_date:
                query = query.filter(Event.event_end_date <= end_date)
            if entity_id is not None:
                entity_ids = [entity_id]
                if include_children:
                    requesting_member = self.db.query(EntityMember).filter(
                        EntityMember.entity_id == entity_id,
                        EntityMember.member_id == requester_member_id
                    ).first()

                    # Only check role if the member exists in this entity
                    if requesting_member is not None:
                        requesting_member_entity_role = requesting_member.member_entity_role_id
                        # If the requesting member is a Leader, Assistant leader, or Secretary
                        if requesting_member_entity_role in [1, 2, 4]:
                            entity_ids = EntityRepository(self.db).get_descendant_entity_ids(
                                entity_id, include_self=True
                            )
                query = query.filter(
                    or_(
                        Event.organizing_entity_id.in_(entity_ids),
                        Event.event_entities.any(
                            EventEntity.entity_id.in_(entity_ids)),
                    ))
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
            new_event.created_at = get_egypt_time()
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

            organizing_entity_members = self.db.query(Entity).filter(
                Entity.entity_id == event["organizing_entity_id"]).first().members

            added_member_ids: set[str] = set()

            def add_member_attendance(member) -> None:
                if member is None or not getattr(member, "member_id", None):
                    return
                member_key = str(member.member_id).strip().upper()
                if not member_key or member_key in added_member_ids:
                    return
                added_member_ids.add(member_key)
                member_attendance = Attendance()
                member_attendance.event_id = new_event.event_id
                member_attendance.member_id = member.member_id
                member_attendance.attendance_state_id = not_specified_state.attendance_state_id
                new_event.attendance_records.append(member_attendance)

            for member in organizing_entity_members:
                add_member_attendance(member)

            logger.info(f"is_multi_team: {event.get('is_multi_team')}")
            logger.info(
                f"participating_entities_ids: {event.get('participating_entities_ids')}")
            logger.info(f"Event dict keys: {event.keys()}")

            if event.get("is_multi_team") and event.get("participating_entities_ids"):
                for entity_id in event["participating_entities_ids"]:
                    participating_entity = self.db.query(Entity).filter(
                        Entity.entity_id == entity_id).first()
                    participating_entity_members = participating_entity.members
                    # Create event entity record
                    event_entity = EventEntity()
                    event_entity.event_id = new_event.event_id
                    event_entity.entity_id = entity_id
                    new_event.event_entities.append(event_entity)

                    # Create attendance records for members of participating entity
                    for member in participating_entity_members:
                        add_member_attendance(member)

            self.db.commit()

            return new_event
        except SQLAlchemyError as e:
            logger.error(f"Error creating event: {e}")
            raise ServiceError(message=f"Failed to create event: {str(e)}",
                               name="Database Error")

    def update_event(self, event_id: int, event: dict, current_user_id: int) -> Event:
        """Update an existing event."""
        try:
            existing_event = self.db.query(Event).filter(
                Event.event_id == event_id).first()

            existing_event.event_name_en = event.get(
                "event_name", {}).get("en", existing_event.event_name_en)
            existing_event.event_name_ar = event.get(
                "event_name", {}).get("ar", existing_event.event_name_ar)
            existing_event.event_start_date = event.get(
                "event_start_date", existing_event.event_start_date)
            existing_event.event_end_date = event.get(
                "event_end_date", existing_event.event_end_date)
            existing_event.event_location = event.get(
                "event_location", existing_event.event_location)
            existing_event.is_multi_team = event.get(
                "is_multi_team", existing_event.is_multi_team)
            existing_event.event_type_id = event.get(
                "event_type_id", existing_event.event_type_id)
            existing_event.organizing_entity_id = event.get(
                "organizing_entity_id", existing_event.organizing_entity_id)
            # Update participating_entities via IDs if provided
            participating_entities_ids = event.get(
                "participating_entities_ids", None)
            if participating_entities_ids is not None:
                # Clear existing participating entities
                existing_event.event_entities.clear()

                # Add new participating entities
                for entity_id in participating_entities_ids:
                    event_entity = EventEntity()
                    event_entity.event_id = existing_event.event_id
                    event_entity.entity_id = entity_id
                    existing_event.event_entities.append(event_entity)
            existing_event.updated_at = get_egypt_time()
            existing_event.updated_by = current_user_id

            super().update(existing_event)
            return existing_event
        except SQLAlchemyError as e:
            logger.error(f"Error updating event: {e}")
            raise ServiceError(message=f"Failed to update event: {str(e)}",
                               name="Database Error")

    def delete_event(self, event_id: int) -> None:
        """Delete an event."""
        try:
            event_to_delete = self.db.query(Event).filter(
                Event.event_id == event_id).first()

            attendance_records = self.db.query(Attendance).filter(
                Attendance.event_id == event_id).all()

            for attendance in attendance_records:
                super().delete(attendance)

            super().delete(event_to_delete)
        except SQLAlchemyError as e:
            logger.error(f"Error deleting event: {e}")
            raise ServiceError(message=f"Failed to delete event: {str(e)}",
                               name="Database Error")

    def get_event_attendance(self, event_id: int) -> List[Attendance]:
        """Get attendance records for an event."""
        try:
            return self.db.query(Attendance).filter(Attendance.event_id == event_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching event attendance: {e}")
            raise ServiceError(message=f"Failed to fetch event attendance: {str(e)}",
                               name="Database Error")

    def update_event_attendance(self, event_id: int, member_id: str, attendance_state_id: int, current_user_id: int) -> None:
        """Update attendance records for an event."""
        try:
            attendance_record = self.db.query(Attendance).filter(Attendance.event_id == event_id,
                                                                 Attendance.member_id == member_id).first()
            if attendance_record:
                attendance_record.attendance_state_id = attendance_state_id
                attendance_record.updated_at = datetime.now()
                attendance_record.updated_by = current_user_id
                super().update(attendance_record)
        except SQLAlchemyError as e:
            logger.error(f"Error updating event attendance: {e}")
            raise ServiceError(message=f"Failed to update event attendance: {str(e)}",
                               name="Database Error")
