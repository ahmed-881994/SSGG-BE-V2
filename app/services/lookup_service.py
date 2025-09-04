from logging import getLogger
from typing import Dict, List

from sqlalchemy.orm import Session

from app.core.exceptions import EntityDoesNotExistError, ServiceError
from app.repositories.lookup_repository import LookupRepository

logger = getLogger(__name__)

class LookupService:
    """Service class for Lookup table operations."""
    
    def __init__(self, db_session: Session):
        """Initialize LookupService with database session."""
        self.db_session = db_session
        self.lookup_repository = LookupRepository(db_session)

    def get_all_lookups(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get all lookup tables and their values using SQLAlchemy models.
        
        Returns:
            Dict[str, List[Dict[str, str]]]: A dictionary containing lookup table names as keys and their values as lists of dictionaries.
        """
        try:
            data = []

            # Get Event Types
            event_types = self.lookup_repository.get_event_types()
            if event_types:
                event_type_data = {
                    'table_name': 'event_types',
                    'description': 'Event type lookup values',
                    'lookup_values': []
                }
                for event_type in event_types:
                    lookup_entry = {
                        "lookup_id": event_type.event_type_id,
                        "en": event_type.event_type_name_en,
                        "ar": event_type.event_type_name_ar,
                    }
                    event_type_data['lookup_values'].append(lookup_entry)
                data.append(event_type_data)
            
            # Get Entity Roles
            entity_roles = self.lookup_repository.get_entity_roles()
            if entity_roles:
                entity_role_data = {
                    'table_name': 'entity_roles',
                    'description': 'Entity role lookup values',
                    'lookup_values': []
                }
                for role in entity_roles:
                    lookup_entry = {
                        "lookup_id": role.entity_role_id,
                        "en": role.entity_role_name_en,
                        "ar": role.entity_role_name_ar,
                    }
                    entity_role_data['lookup_values'].append(lookup_entry)
                data.append(entity_role_data)
            
            # Get Entity Types
            entity_types = self.lookup_repository.get_entity_types()
            if entity_types:
                entity_type_data = {
                    'table_name': 'entity_types',
                    'description': 'Entity type lookup values',
                    'lookup_values': []
                }
                for entity_type in entity_types:
                    lookup_entry = {
                        "lookup_id": entity_type.entity_type_id,
                        "en": entity_type.entity_type_name_en,
                        "ar": entity_type.entity_type_name_ar,
                    }
                    entity_type_data['lookup_values'].append(lookup_entry)
                data.append(entity_type_data)

            # Get Attendance States
            attendance_states = self.lookup_repository.get_attendance_states()
            if attendance_states:
                attendance_state_data = {
                    'table_name': 'attendance_states',
                    'description': 'Attendance state lookup values',
                    'lookup_values': []
                }
                for state in attendance_states:
                    lookup_entry = {
                        "lookup_id": state.attendance_state_id,
                        "en": state.attendance_state_name_en,
                        "ar": state.attendance_state_name_ar,
                    }
                    attendance_state_data['lookup_values'].append(lookup_entry)
                data.append(attendance_state_data)

            if not data:
                raise EntityDoesNotExistError(
                    message="No lookup tables found", 
                    name="Lookup Retrieval Error"
                )

            return {"lookups": data}

        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving lookup tables: {str(e)}")
            raise ServiceError(
                message=f"Failed to retrieve lookup tables: {str(e)}",
                name="Lookup Retrieval Error"
            )