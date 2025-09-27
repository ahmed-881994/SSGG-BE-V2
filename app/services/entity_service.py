from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.exceptions import (EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.models.entity_member_model import EntityMember
from app.models.member_model import Member
from app.repositories.entity_repository import EntityRepository
from app.schemas.entity_schema import EntityTransfer


class EntityService:
    """Service for Entity operations."""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.entity_repository = EntityRepository(db_session)
        
    def _entity_exists(self, entity_id: int) -> bool:
        """Check if entity exists - private method for internal use."""
        entity = self.entity_repository.get_entity_by_entity_id(entity_id=entity_id)
        return entity is not None

    def _member_exists_in_entity(self, entity_id: int, member_id: str) -> bool:
        """Check if a member exists in an entity - private method for internal use."""
        return self.db_session.query(EntityMember).filter(EntityMember.entity_id == entity_id).filter(EntityMember.member_id == member_id).filter(EntityMember.date_to.is_(None)).first() is not None

    def get_entity(self, entity_id: int) -> Dict[str, Any]:
        """Retrieve an entity by its ID with entity type names."""
        try:
            entity = self.entity_repository.get_entity_by_entity_id(entity_id=entity_id)
            if not entity:
                raise EntityDoesNotExistError(
                    message=f"Entity with ID {entity_id} not found",
                    name="Entity Retrieval Error"
                )
            # Build the hierarchical response structure
            result = {
                "entity_id": entity.entity_id,
                "entity_name": {
                    "en": entity.entity_name_en,
                    "ar": entity.entity_name_ar
                },
                "entity_parent_id": entity.entity_parent_id,
                "entity_type": {
                    "entity_type_id": entity.entity_type.entity_type_id,
                    "entity_type_name": {
                        "en": entity.entity_type.entity_type_name_en,
                        "ar": entity.entity_type.entity_type_name_ar
                } if entity.entity_type else None
            }}
            
            # Add children if they exist
            if hasattr(entity, 'children') and entity.children:
                result["children"] = [
                    {
                        "entity_id": child.entity_id,
                        "entity_name": {
                            "en": child.entity_name_en,
                            "ar": child.entity_name_ar
                        },
                        "entity_parent_id": child.entity_parent_id,
                        "entity_type": {
                            "entity_type_id": child.entity_type.entity_type_id,
                            "entity_type_name": {
                                "en": child.entity_type.entity_type_name_en,
                                "ar": child.entity_type.entity_type_name_ar
                        } if child.entity_type else None
                    }
                    }
                    for child in entity.children
                ]
            else:
                result["children"] = []
            
            # Add parent if it exists
            if hasattr(entity, 'parent') and entity.parent:
                result["parent"] = {
                    "entity_id": entity.parent.entity_id,
                    "entity_name": {
                        "en": entity.parent.entity_name_en,
                        "ar": entity.parent.entity_name_ar
                    },
                    "entity_parent_id": entity.parent.entity_parent_id,
                    "entity_type": {
                        "entity_type_id": entity.parent.entity_type.entity_type_id,
                        "entity_type_name": {
                            "en": entity.parent.entity_type.entity_type_name_en,
                            "ar": entity.parent.entity_type.entity_type_name_ar
                        } if entity.parent.entity_type else None
                }}
            else:
                result["parent"] = None
            
            return result
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving entity: {entity_id}: {str(e)}")
            raise ServiceError(
                message=f"Failed to retrieve entity: {str(e)}",
                name="Entity Retrieval Error"
            )
            
    def get_entity_members(
        self, 
        entity_id: int, 
        include_inactive: bool = False,
        role_id: Optional[int] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get all members for an entity."""
        
        logger.info(f"Getting members for entity {entity_id}")
        try:
            # Check entity existence first
            if not self._entity_exists(entity_id):
                raise EntityDoesNotExistError(
                    message=f"Entity with ID {entity_id} not found",
                    name="Entity Retrieval Error"
                )

            entity_members = self.entity_repository.get_entity_members(entity_id, include_inactive, role_id)

            return {'members': [
                {
                    'member_id': em.member_id,
                    'member_name': {
                        'en': f"{em.member.name_en}".strip() if em.member else None,
                        'ar': f"{em.member.name_ar}".strip() if em.member else None
                    },
                    'role_id': em.member_entity_role_id,
                    'role_name': {
                        'en': em.role.entity_role_name_en if hasattr(em, 'role') and em.role else None,
                        'ar': em.role.entity_role_name_ar if hasattr(em, 'role') and em.role else None
                    },
                    'date_from': em.date_from if em.date_from else None,
                    'date_to': em.date_to if em.date_to else None,
                    'is_active': em.date_to is None
                }
                for em in entity_members
            ]}

        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving entity members for {entity_id}: {str(e)}")
            raise ServiceError(
                message=f"Failed to retrieve entity members: {str(e)}",
                name="Entity Members Retrieval Error"
            )

    def search_entities(self, entity_id: Optional[int] = None, entity_parent_id: Optional[int] = None, entity_name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Search for entities based on various criteria."""
        logger.info(f"Searching entities with ID: {entity_id}, Parent ID: {entity_parent_id}, Name: {entity_name}")
        try:
            entities = self.entity_repository.search_entities(entity_id, entity_parent_id, entity_name)
            if not entities:
                raise EntityDoesNotExistError(
                    message="No entities found matching the search criteria",
                    name="Entity Search Error"
                )
            return {"entities":[{
                "entity_id": entity.entity_id,
                "entity_name": {
                    "en": entity.entity_name_en,
                    "ar": entity.entity_name_ar
                },
                "parent_id": entity.entity_parent_id,
                "entity_type": {
                    "entity_type_id": entity.entity_type_id,
                    "entity_type_name": {
                        "en": entity.entity_type.entity_type_name_en,
                        "ar": entity.entity_type.entity_type_name_ar
                    }
                }
            } for entity in entities]}
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error searching entities: {str(e)}")
            raise ServiceError(
                message=f"Failed to search entities: {str(e)}",
                name="Entity Search Error"
            )
            
    def create_entity(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new entity."""
        logger.info(f"Creating entity with data: {entity_data}")
        try:
            # Check entity existence
            # if self._entity_exists(entity_data["entity_id"]):
            #     raise EntityAlreadyExistsError(
            #         message=f"Entity with ID {entity_data['entity_id']} already exists",
            #         name="Entity Creation Error"
            #     )

            entity_id = self.entity_repository.get_next_entity_id()

            # Check parent entity exists if provided
            if entity_data.get("parent_id"):
                if not self._entity_exists(entity_data["parent_id"]):
                    raise EntityDoesNotExistError(
                        message=f"Parent entity with ID {entity_data['parent_id']} not found",
                        name="Entity Creation Error"
                    )
                    
            entity = self.entity_repository.create_entity(
                entity_id=entity_id,
                entity_name_en=entity_data["entity_name"]["en"],
                entity_name_ar=entity_data["entity_name"]["ar"],
                entity_parent_id=entity_data["parent_id"],
                entity_type_id=entity_data["entity_type"]
            )
            return {
                "entity_id": entity.entity_id,
                "entity_name": {
                    "en": entity.entity_name_en,
                    "ar": entity.entity_name_ar
                },
                "parent_id": entity.entity_parent_id,
                "entity_type": {
                    "entity_type_id": entity.entity_type_id,
                    "entity_type_name": {
                        "en": entity.entity_type.entity_type_name_en,
                        "ar": entity.entity_type.entity_type_name_ar
                    }
                }
            }
        except EntityAlreadyExistsError:
            raise
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error creating entity: {str(e)}")
            raise ServiceError(
                message=f"Failed to create entity: {str(e)}",
                name="Entity Creation Error"
            )

    def assign_member_to_entity(self, entity_id: int, memberships: List[dict]) -> bool:
        """
        Add a member to an entity.

        Args:
            entity_id (int): The ID of the entity.
            memberships (List[dict]): A list of membership details.

        Returns:
            bool: True if the operation was successful, False otherwise.

        Raises:
            EntityDoesNotExistError: If the entity does not exist.
            ServiceError: If there is a service-related error.
        """
        logger.info(f"Adding members to entity {entity_id}")
        try:
            if not self._entity_exists(entity_id):
                raise EntityDoesNotExistError(
                    message=f"Entity with ID {entity_id} not found",
                    name="Entity ID"
                )
            for membership in memberships:
                member_id = membership.get("member_id")
                role_id = membership.get("role_id")
                from_date = membership.get("from_date")

                
            
                # Validate member existence
                member = self.db_session.query(Member).filter(Member.member_id == member_id).first()
                if not member:
                    raise EntityDoesNotExistError(
                        message=f"Member with ID {member_id} not found",
                        name="Member ID"
                    )
                    
                # Validate role existence
                if not self.entity_repository.role_exists(role_id):
                    raise EntityDoesNotExistError(
                        message=f"Role with ID {role_id} not found",
                        name="Role ID"
                    )
                    

                # If member already has this exact role actively, skip this assignment
                if self.entity_repository.get_active_member_assignment(entity_id, member_id, role_id):
                    logger.warning(f"Member {member_id} already has an active assignment with role {role_id} in entity {entity_id}. Skipping.")
                    continue    
                
                # Check for existing active assignment
                existing_any_role_assignment = self.entity_repository.get_active_member_assignment(entity_id, member_id)
                # If there's an existing active assignment, update its end date
                if existing_any_role_assignment:
                    # Update the existing assignment's end date
                    self.entity_repository.update_member_assignment_end_date(existing_any_role_assignment, from_date)

                    logger.info(f"Ended existing assignment for member {member_id} in entity {entity_id} on {from_date}")

                    self.entity_repository.assign_member_to_entity(
                        entity_id=entity_id,
                        member_id=member_id,
                        role_id=role_id,
                        from_date=from_date
                    )
                    
                    logger.info(f"Created new assignment for member {member_id} in entity {entity_id} with role {role_id}")
                else:
                    self.entity_repository.assign_member_to_entity(
                        entity_id=entity_id,
                        member_id=member_id,
                        role_id=role_id,
                        from_date=from_date
                    )
            return True
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error adding member to entity: {str(e)}")
            raise ServiceError(
                message=f"Failed to add member to entity: {str(e)}",
                name="Entity Member Addition Error"
            )


    def update_entity_member_role(self, entity_id: int, body: dict) -> bool:
        """
        Update the role of a member in an entity.

        Args:
            entity_id: The ID of the entity.
            body: A dictionary containing the member ID and the new role ID.

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            EntityDoesNotExistError: If the member is not part of the entity.
            ServiceError: If the update fails.
        """
        member_id = body.get("member_id")
        new_role_id = body.get("role_id")

        try:
            # Check if the member is part of the entity
            existing_assignment = self.entity_repository.get_active_member_assignment(entity_id, member_id)

            if not existing_assignment:
                logger.warning(f"Member {member_id} is not part of entity {entity_id}.")
                raise EntityDoesNotExistError(
                    message=f"Member {member_id} is not part of entity {entity_id}.",
                    name="Entity Member Role Update Error"
                )

            # Update the role through repository
            success = self.entity_repository.update_member_role(entity_id, member_id, new_role_id)
            
            if success:
                logger.info(f"Updated role for member {member_id} in entity {entity_id} to {new_role_id}.")
                return True
            else:
                raise ServiceError(
                    message=f"Failed to update role for member {member_id} in entity {entity_id}",
                    name="Entity Member Role Update Error"
                )
                
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error updating member role in entity: {str(e)}")
            raise ServiceError(
                message=f"Failed to update member role in entity: {str(e)}",
                name="Entity Member Role Update Error"
            )

    def transfer_entity_members(self, entity_transfer_data: List[EntityTransfer]) -> bool:
        """
        Transfer members between entities.

        Args:
            entity_id: The ID of the entity to transfer members from.
            body: A list of EntityTransfer objects containing the target entity ID and member IDs.

        Returns:
            bool: True if the transfer was successful, False otherwise.

        Raises:
            EntityDoesNotExistError: If the entity or members do not exist.
            ServiceError: If the transfer fails.
        """
        try:
            for transfer in entity_transfer_data:
                source_entity_id = transfer.from_entity_id
                target_entity_id = transfer.to_entity_id
                member_id = transfer.member_id

                # Check if the target entity exists
                if not self._entity_exists(target_entity_id):
                    logger.warning(f"Target entity {target_entity_id} does not exist.")
                    raise EntityDoesNotExistError(
                        message=f"Target entity {target_entity_id} does not exist.",
                        name="Entity Transfer Error"
                    )

                # Check if the member is part of the source entity
                if not self._member_exists_in_entity(source_entity_id, member_id):
                    logger.warning(f"Member {member_id} is not part of entity {source_entity_id}.")
                    continue

                # End membership in the source entity
                self.entity_repository.end_member_membership(
                    entity_id=source_entity_id,
                    member_id=member_id,
                    end_date=transfer.transfer_date
                )

                # Transfer the member to the target entity
                self.entity_repository.assign_member_to_entity(
                        entity_id=target_entity_id,
                        member_id=member_id,
                        role_id=transfer.role_id,
                        from_date=transfer.transfer_date
                    )

            return True
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error transferring entity members: {str(e)}")
            raise ServiceError(
                message=f"Failed to transfer entity members: {str(e)}",
                name="Entity Member Transfer Error"
            )


    def update_entity(self, entity_id: int, entity_data: dict) -> Dict[str, Any]:
        """Update an existing entity."""
        try:
            if not self._entity_exists(entity_id):
                raise EntityDoesNotExistError(
                    message=f"Entity with ID {entity_id} does not exist.",
                    name="Entity Update Error"
                )
                
            # Fetch existing entity to use current names as defaults
            existing_entity = self.entity_repository.get_entity_by_entity_id(entity_id)
            entity_name_en = entity_data.get("entity_name", {}).get("en")
            if not entity_name_en:
                entity_name_en = getattr(existing_entity, "entity_name_en", None)
            entity_name_ar = entity_data.get("entity_name", {}).get("ar")
            if not entity_name_ar:
                entity_name_ar = getattr(existing_entity, "entity_name_ar", None)

            # Update entity fields
            self.entity_repository.update_entity(
                entity_id=entity_id,
                entity_name_en=entity_name_en,
                entity_name_ar=entity_name_ar,
                entity_parent_id=entity_data.get("parent_id", None),
                entity_type_id=entity_data.get("entity_type", None)
            )
            return self.get_entity(entity_id) 
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error updating entity: {str(e)}")
            raise ServiceError(
                message=f"Failed to update entity: {str(e)}",
                name="Entity Update Error"
            )

    def delete_entity(self, entity_id: int) -> bool:
        """Delete an entity."""
        try:
            if not self._entity_exists(entity_id):
                raise EntityDoesNotExistError(
                    message=f"Entity with ID {entity_id} does not exist.",
                    name="Entity Delete Error"
                )

            self.entity_repository.delete_entity_members(entity_id)
            self.entity_repository.delete_entity(entity_id)

            return True
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error deleting entity: {str(e)}")
            raise ServiceError(
                message=f"Failed to delete entity: {str(e)}",
                name="Entity Delete Error"
            )
            
    def get_entity_attendance(self, entity_id: int):
        """Get attendance data for an entity."""
        try:
            entity = self.entity_repository.get_entity_by_entity_id(entity_id)
            if entity is None:
                raise EntityDoesNotExistError(
                    message=f"Entity with ID {entity_id} does not exist.",
                    name="Entity Attendance Retrieval Error"
                )
            entity_events = entity.all_events
            total_events = len(entity_events)
            attended_events = 0
            attendance_records_count = 0
            
            entity_attendance = {
                "events": [
                    {
                        "event_id": event.event_id,
                        "event_name": {
                            "en": event.event_name_en,
                            "ar": event.event_name_ar
                        },
                        "event_start_date": event.event_start_date,
                        "event_end_date": event.event_end_date,
                        "attendance": [
                            {
                                "member_id": attendance.member.member_id,
                                "member_name": {
                                    "en": attendance.member.name_en,
                                    "ar": attendance.member.name_ar
                                } if attendance.member else None,
                                "attendance_state": {
                                    "attendance_state_id": attendance.attendance_state.attendance_state_id,
                                    "attendance_state_name": {
                                        "en": attendance.attendance_state.attendance_state_name_en,
                                        "ar": attendance.attendance_state.attendance_state_name_ar
                                    } if attendance.attendance_state else None
                                } if attendance.attendance_state else None
                            }
                            for attendance in event.attendance_records
                        ] if hasattr(event, 'attendance_records') else []
                    }
                    for event in entity_events
                ],
                "total_events": 0,  # Direct assignment of int
                "attendance_percentage": 0.0  # Direct assignment of float
            }
            # Calculate attendance statistics
            for event in entity_events:
                attendance_records_count += len(event.attendance_records)
                attended_events += sum(1 for attendance in event.attendance_records if attendance.attendance_state_id in [1, 4])  # Assuming 1 and 4 are the IDs for attended states

            attendance_percentage = (attended_events / attendance_records_count * 100) if attendance_records_count > 0 else 0

            entity_attendance["total_events"] = total_events
            entity_attendance["attendance_percentage"] = attendance_percentage
            return entity_attendance
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving entity attendance: {str(e)}")
            raise ServiceError(
                message=f"Failed to retrieve entity attendance: {str(e)}",
                name="Entity Attendance Retrieval Error"
            )
