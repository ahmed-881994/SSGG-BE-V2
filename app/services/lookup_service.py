from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.exceptions import EntityDoesNotExistError, ServiceError
from app.repositories.lookup_repository import LookupRepository


class LookupService:
    """Service class for Lookup table operations."""
    
    def __init__(self, db_session: Session):
        """Initialize LookupService with database session."""
        self.db_session = db_session
        self.lookup_repository = LookupRepository(db_session)


    def _format_lookup_entry(self, entries, table_name) -> Dict[str, Any]:
        """
        Format a single lookup entry into a dictionary.
        """
        formatted_table_name = table_name.replace("_", " ").title()
        formatted_entry = {
            'table_name': table_name,
            'description': f"{formatted_table_name} lookup values",
            'lookup_values': []
        }
        table_name = table_name[:-1] if table_name.endswith('s') else table_name  # Remove trailing 's' for singular form  
        for entry in entries:
            formatted_entry["lookup_values"].append({
                "lookup_id": getattr(entry, f"{table_name}_id"),
                "en": getattr(entry, f"{table_name}_name_en"),
                "ar": getattr(entry, f"{table_name}_name_ar")
            })
        return formatted_entry

    def get_all_lookups(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get all lookup tables and their values using SQLAlchemy models.
        
        Returns:
            Dict[str, List[Dict[str, str]]]: A dictionary containing lookup table names as keys and their values as lists of dictionaries.
        """
        logger.debug("Retrieving all lookup tables")
        try:
            lookup_data = []

            # Get Event Types
            event_types = self.lookup_repository.get_event_types()
            if event_types:
                event_type_data = self._format_lookup_entry(event_types, "event_types")
                lookup_data.append(event_type_data)

            # Get Entity Roles
            entity_roles = self.lookup_repository.get_entity_roles()
            if entity_roles:
                entity_role_data = self._format_lookup_entry(entity_roles, "entity_roles")
                lookup_data.append(entity_role_data)
            
            # Get Entity Types
            entity_types = self.lookup_repository.get_entity_types()
            if entity_types:
                entity_type_data = self._format_lookup_entry(entity_types, "entity_types")
                lookup_data.append(entity_type_data)

            # Get Attendance States
            attendance_states = self.lookup_repository.get_attendance_states()
            if attendance_states:
                attendance_state_data = self._format_lookup_entry(attendance_states, "attendance_states")
                lookup_data.append(attendance_state_data)

            if not lookup_data:
                logger.warning("No lookup tables found")
                raise EntityDoesNotExistError(
                    message="No lookup tables found", 
                    name="Lookup Retrieval Error"
                )

            return {"lookups": lookup_data}

        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving lookup tables: {str(e)}")
            raise ServiceError(
                message=f"Failed to retrieve lookup tables: {str(e)}",
                name="Lookup Retrieval Error"
            )