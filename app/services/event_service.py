from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.exceptions import EntityDoesNotExistError, ServiceError
from app.repositories.event_repository import EventRepository


class EventService:
    """Service for Event operations."""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.event_repository = EventRepository(db_session)
        
    def _format_event_data(self, event: Any) -> Dict[str, Any]:
        """Format event data for output."""
        return {
            "event_id": event.event_id,
            "event_name": {
                "en": event.event_name_en,
                "ar": event.event_name_ar
            },
            "event_start_date": event.event_start_date,
            "event_end_date": event.event_end_date,
            "event_location": event.event_location,
            "is_multi_team": event.is_multi_team,
            "event_type": {
                "event_type_id": event.event_type.event_type_id,
                "event_type_name": {
                    "en": event.event_type.event_type_name_en,
                    "ar": event.event_type.event_type_name_ar
                }
            },
            "organizing_entity": {
                "entity_id": event.organizing_entity.entity_id,
                "entity_name": {
                    "en": event.organizing_entity.entity_name_en,
                    "ar": event.organizing_entity.entity_name_ar
                }
            },
            "participating_entities": [{
                "entity_id": entity.entity_id,
                "entity_name": {
                    "en": entity.entity_name_en,
                    "ar": entity.entity_name_ar
                }
            } for entity in event.participating_entities]
        }

    def get_event_by_event_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get an event by its ID."""
        logger.info(f"Getting event by ID: {event_id}")
        try:
            event = self.event_repository.get_event_by_event_id(event_id)
            if not event:
                logger.warning(f"Event not found: {event_id}")
                raise EntityDoesNotExistError(
                    f"Event with ID {event_id} does not exist.", name="Event Retrieval Error")
            return self._format_event_data(event)
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving event: {event_id}: {str(e)}")
            raise ServiceError(
                message=f"Failed to retrieve event: {str(e)}",
                name="Event Retrieval Error"
            )

    def search_events(self, name: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, entity_id: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Search for events based on various criteria."""
        logger.info(f"Searching events: name={name}, start_date={start_date}, end_date={end_date}, entity_id={entity_id}")
        try:
            events = self.event_repository.search_events(name=name, start_date=start_date, end_date=end_date, entity_id=entity_id)
            if not events:
                logger.info("No events found matching the criteria.")
                raise EntityDoesNotExistError("No events found matching the criteria.")
            return {"events": [self._format_event_data(event) for event in events]}
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error searching events: {str(e)}")
            raise ServiceError(
                message=f"Failed to search events: {str(e)}",
                name="Event Search Error"
            )

    def create_event(self, event_data: Dict[str, Any], current_user_id: int) -> Dict[str, Any]:
        """Create a new event."""
        logger.info(f"Creating event: {event_data}")
        try:
            new_event = self.event_repository.create_event(event_data, current_user_id=current_user_id)
            return self._format_event_data(new_event)
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            raise ServiceError(
                message=f"Failed to create event: {str(e)}",
                name="Event Creation Error"
            )
            
    def update_event(self, event_id: int, update_data: Dict[str, Any], current_user_id: int) -> Dict[str, Any]:
        """Update an existing event."""
        logger.info(f"Updating event {event_id} with data: {update_data}")
        try:
            existing_event = self.event_repository.get_event_by_event_id(event_id)
            if not existing_event:
                raise EntityDoesNotExistError(
                    f"Event with ID {event_id} does not exist.", name="Event Retrieval Error"
                )
            updated_event = self.event_repository.update_event(event_id, update_data, current_user_id)
            return self._format_event_data(updated_event)
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error updating event {event_id}: {str(e)}")
            raise ServiceError(
                message=f"Failed to update event: {str(e)}",
                name="Event Update Error"
            )
            
    def delete_event(self, event_id: int) -> None:
        """Delete an event."""
        logger.info(f"Deleting event: {event_id}")
        try:
            event_to_delete = self.event_repository.get_event_by_event_id(event_id)
            if not event_to_delete:
                raise EntityDoesNotExistError(message="Event not found", name="Not Found Error")

            self.event_repository.delete_event(event_id)
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error deleting event {event_id}: {str(e)}")
            raise ServiceError(
                message=f"Failed to delete event: {str(e)}",
                name="Event Deletion Error"
            )

    def get_event_attendance(self, event_id: int) -> Dict[str, Any]:
        """Get attendance records for an event."""
        logger.info(f"Getting attendance for event: {event_id}")
        try:
            event = self.event_repository.get_event_by_event_id(event_id)
            if not event:
                raise EntityDoesNotExistError(
                    f"Event with ID {event_id} does not exist.", name="Event Retrieval Error"
                )
            attendance_records = self.event_repository.get_event_attendance(event_id)
            return {
                "event_id": event.event_id,
                "event_name": {
                    "en": event.event_name_en,
                    "ar": event.event_name_ar
                },
                "attendance_records": [
                    {
                        "member_id": record.member.member_id,
                        "member_name": {
                            "en": record.member.name_en,
                            "ar": record.member.name_ar
                        },
                        "attendance_state": {
                            "attendance_state_id": record.attendance_state.attendance_state_id,
                            "attendance_state_name": {
                                "en": record.attendance_state.attendance_state_name_en,
                                "ar": record.attendance_state.attendance_state_name_ar
                            }
                        }
                    } for record in attendance_records
                ]
            }
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving attendance for event {event_id}: {str(e)}")
            raise ServiceError(
                message=f"Failed to retrieve event attendance: {str(e)}",
                name="Event Attendance Retrieval Error"
            )

    def update_event_attendance(self, event_id: int, attendance_data: dict, current_user_id: int) -> None:
        """Update attendance records for an event."""
        logger.info(f"Updating attendance for event: {event_id}")
        try:
            event = self.event_repository.get_event_by_event_id(event_id)
            if not event:
                raise EntityDoesNotExistError(
                    f"Event with ID {event_id} does not exist.", name="Event Retrieval Error"
                )

            for record in attendance_data.get("attendance", []):
                member_id = record.get("member_id")
                attendance_state_id = record.get("attendance_state_id")
                if not member_id or not attendance_state_id:
                    logger.warning(f"Skipping attendance record for event {event_id} due to missing required fields: {record}")
                    continue

                self.event_repository.update_event_attendance(event_id, member_id, attendance_state_id, current_user_id)
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error updating attendance for event {event_id}: {str(e)}")
            raise ServiceError(
                message=f"Failed to update event attendance: {str(e)}",
                name="Event Attendance Update Error"
            )