from typing import List

from sqlalchemy.orm import Session

from app.models.attendance_state_model import AttendanceState
from app.models.entity_role_model import EntityRole
from app.models.entity_type_model import EntityType
from app.models.event_type_model import EventType


class LookupRepository:
    """Repository for Lookup table operations."""
    
    def __init__(self, db_session: Session):
        """Initialize LookupRepository with database session."""
        self.db = db_session
    
    def get_event_types(self) -> List[EventType]:
        """Get all event types."""
        return self.db.query(EventType).all()
    
    def get_entity_roles(self) -> List[EntityRole]:
        """Get all entity roles."""
        return self.db.query(EntityRole).all()
    
    def get_entity_types(self) -> List[EntityType]:
        """Get all entity types."""
        return self.db.query(EntityType).all()
    
    def get_attendance_states(self) -> List[AttendanceState]:
        """Get all attendance statuses."""
        return self.db.query(AttendanceState).all()