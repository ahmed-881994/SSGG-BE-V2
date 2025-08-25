from logging import getLogger
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import ServiceError
from app.models.entity_model import Entity
from app.models.event_model import Event
from app.repositories.base_repository import BaseRepository

logger = getLogger(__name__)

class EventRepository(BaseRepository[Event]):
    """Repository for Event database operations."""

    def __init__(self, db_session: Session):
        super().__init__(db_session, Event)


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