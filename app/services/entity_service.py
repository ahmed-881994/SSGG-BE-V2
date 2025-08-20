
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.config.logging_config import logger
from app.core.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError, ServiceError
from app.models.entity_member import EntityMember
from app.models.entity_role import EntityRole
from app.models.member import Member
from app.repositories.entity_repository import EntityRepository
from app.schemas.entity import EntityTransfer


class EntityService:
    """Service for Entity operations."""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.entity_repository = EntityRepository(db_session)
        
    def _entity_exists(self, entity_id: int) -> bool:
        """Check if entity exists - private method for internal use."""
        entity = self.entity_repository.get_entity_by_id(entity_id=entity_id)
        return entity is not None

    def _member_exists_in_entity(self, entity_id: int, member_id: str) -> bool:
        """Check if a member exists in an entity - private method for internal use."""
        return self.db_session.query(EntityMember).filter(EntityMember.entity_id == entity_id).filter(EntityMember.member_id == member_id).filter(EntityMember.date_to == None).first() is not None

    def get_entity(self, entity_id: int) -> Dict[str, Any]:
        """Retrieve an entity by its ID with entity type names."""
        try:
            entity = self.entity_repository.get_entity_by_id(entity_id=entity_id)
            if not entity:
                raise EntityDoesNotExistError(
                    message=f"Entity with ID {id} not found",
                    name="Entity Retrieval Error"
                )
            return entity.to_dict(include_relationships=True)
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving user {id}: {str(e)}")
            raise ServiceError(
                message=f"Failed to retrieve entity: {str(e)}",
                name="Entity Retrieval Error"
            )
            
    def get_entity_members(
        self, 
        entity_id: int, 
        include_inactive: bool = False,
        role_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
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
            
            return [
                {
                    'member_id': em.member_id,
                    'member_name_en': f"{em.member.name_en}".strip() if em.member else None,
                    'member_name_ar': f"{em.member.name_ar}".strip() if em.member else None,
                    'role_id': em.member_entity_role_id,
                    'role_name_en': em.role.entity_role_name_en if hasattr(em, 'role') and em.role else None,
                    'role_name_ar': em.role.entity_role_name_ar if hasattr(em, 'role') and em.role else None,
                    'date_from': em.date_from if em.date_from else None,
                    'date_to': em.date_to if em.date_to else None,
                    'is_active': em.date_to is None
                }
                for em in entity_members
            ]
        
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving entity members for {entity_id}: {str(e)}")
            raise ServiceError(
                message=f"Failed to retrieve entity members: {str(e)}",
                name="Entity Members Retrieval Error"
            )

    def search_entities(self, entity_id: Optional[int] = None, entity_parent_id: Optional[int] = None, entity_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for entities based on various criteria."""
        logger.info(f"Searching entities with ID: {entity_id}, Parent ID: {entity_parent_id}, Name: {entity_name}")
        try:
            entities = self.entity_repository.search_entities(entity_id, entity_parent_id, entity_name)
            if not entities:
                raise EntityDoesNotExistError(
                    message="No entities found matching the search criteria",
                    name="Entity Search Error"
                )
            return [entity.to_dict() for entity in entities]
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
            if self._entity_exists(entity_data["entity_id"]):
                raise EntityAlreadyExistsError(
                    message=f"Entity with ID {entity_data['entity_id']} already exists",
                    name="Entity Creation Error"
                )
                
            # Check parent entity exists if provided
            if entity_data.get("entity_parent_id"):
                if not self._entity_exists(entity_data["entity_parent_id"]):
                    raise EntityDoesNotExistError(
                        message=f"Parent entity with ID {entity_data['entity_parent_id']} not found",
                        name="Entity Creation Error"
                    )
                    
            entity = self.entity_repository.create_entity(
                entity_id=entity_data["entity_id"],
                entity_name_en=entity_data["entity_name_en"],
                entity_name_ar=entity_data["entity_name_ar"],
                entity_parent_id=entity_data["entity_parent_id"],
                entity_type_id=entity_data["entity_type_id"]
            )
            return entity.to_dict()
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
                role = self.db_session.query(EntityRole).filter(EntityRole.id == role_id).first()
                if not role:
                    raise EntityDoesNotExistError(
                        message=f"Role with ID {role_id} not found",
                        name="Role ID"
                    )
                    
                
                # Check for existing active assignment with the SAME ROLE
                existing_same_role_assignment = (
                    self.db_session.query(EntityMember)
                    .filter(
                        and_(
                            EntityMember.entity_id == entity_id,
                            EntityMember.member_id == member_id,
                            EntityMember.member_entity_role_id == role_id,  # Same role check
                            EntityMember.date_to.is_(None)  # Active assignment
                        )
                    )
                    .first()
                )
                
                # If member already has this exact role actively, skip this assignment
                if existing_same_role_assignment:
                    logger.warning(f"Member {member_id} already has an active assignment with role {role_id} in entity {entity_id}. Skipping.")
                    continue
                
                
                
                # Parse from_date or use today
                if from_date:
                    try:
                        parsed_from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
                    except ValueError:
                        raise ServiceError(
                            message=f"Invalid date format: {from_date}. Expected YYYY-MM-DD",
                            name="Date Format Error"
                        )
                else:
                    parsed_from_date = date.today()
                    
                
                # Check for existing active assignment
                existing_any_role_assignment = (
                    self.db_session.query(EntityMember)
                    .filter(
                        and_(
                            EntityMember.entity_id == entity_id,
                            EntityMember.member_id == member_id,
                            EntityMember.date_to.is_(None)  # Active assignment
                        )
                    )
                    .first()
                )
                # If there's an existing active assignment, update its end date
                if existing_any_role_assignment:
                    # Update the existing assignment's end date
                    existing_any_role_assignment.date_to = parsed_from_date
                    self.db_session.commit()  # Ensure the update is committed
                    self.db_session.refresh(existing_any_role_assignment)  # Refresh to get updated fields

                    logger.info(f"Ended existing assignment for member {member_id} in entity {entity_id} on {from_date}")

                    self.entity_repository.assign_member_to_entity(
                        entity_id=entity_id,
                        member_id=member_id,
                        role_id=role_id,
                        from_date=parsed_from_date
                    )
                    
                    logger.info(f"Created new assignment for member {member_id} in entity {entity_id} with role {role_id}")
                else:
                    self.entity_repository.assign_member_to_entity(
                        entity_id=entity_id,
                        member_id=member_id,
                        role_id=role_id,
                        from_date=parsed_from_date
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
            existing_assignment = (
                self.db_session.query(EntityMember)
                .filter(
                    EntityMember.entity_id == entity_id,
                    EntityMember.member_id == member_id,
                    EntityMember.date_to.is_(None)  # Active assignment
                )
                .first()
            )

            if not self._member_exists_in_entity(entity_id, member_id):
                logger.warning(f"Member {member_id} is not part of entity {entity_id}.")
                raise EntityDoesNotExistError(
                    message=f"Member {member_id} is not part of entity {entity_id}.",
                    name="Entity Member Role Update Error"
                )

            # Update the role ID
            existing_assignment.member_entity_role_id = new_role_id
            self.db_session.commit()
            self.db_session.refresh(existing_assignment)

            logger.info(f"Updated role for member {member_id} in entity {entity_id} to {new_role_id}.")
            return True
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
                    # raise EntityDoesNotExistError(
                    #         message=f"Member {member_id} is not part of entity {entity_id}.",
                    #         name="Entity Transfer Error"
                    #     )

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