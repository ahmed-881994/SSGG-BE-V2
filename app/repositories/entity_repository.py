from datetime import datetime
from logging import getLogger
from typing import List, Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.models.entity_model import Entity
from app.models.entity_member_model import EntityMember
from app.repositories.base_repository import BaseRepository

logger = getLogger(__name__)

class EntityRepository(BaseRepository[Entity]):
    """Repository for Entity database operations."""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, Entity)

    def get_entity_by_id(self, entity_id: int) -> Entity | None:

        try:
            # entity = self.get_by_id(id)
            return self.db.query(Entity).filter(Entity.entity_id == entity_id).first()
        except SQLAlchemyError as e:
            raise ServiceError(
                message=f"Failed to retrieve entity: {str(e)}",
                name="Database Error"
            )
            
    def get_next_entity_id(self) -> int:
        """Get the next available entity ID."""
        try:
            return (self.db.query(func.max(Entity.entity_id)).scalar() or 0) + 1
        except SQLAlchemyError as e:
            raise ServiceError(
                message=f"Failed to retrieve next entity ID: {str(e)}",
                name="Database Error"
            )

    def get_entity_members(self, entity_id: int, include_inactive: bool = False, role_id: Optional[int] = None) -> List[EntityMember]:
        """Get all members for an entity with optional filters."""
        try:
            query = (
                self.db.query(EntityMember)
                .filter(EntityMember.entity_id == entity_id)
            )
            
            if not include_inactive:
                query = query.filter(EntityMember.date_to.is_(None))
            
            if role_id:
                query = query.filter(EntityMember.member_entity_role_id == role_id)

            return query.all()
        except SQLAlchemyError as e:
            raise ServiceError(
                message=f"Failed to retrieve entity: {str(e)}",
                name="Database Error"
            )

    def search_entities(self, entity_id: Optional[int] = None, entity_parent_id: Optional[int] = None, entity_name: Optional[str] = None) -> List[Entity]:
        """Search for entities based on various criteria."""
        try:
            query = self.db.query(Entity)

            if entity_id:
                query = query.filter(Entity.entity_id == entity_id)
            if entity_parent_id:
                query = query.filter(Entity.entity_parent_id == entity_parent_id)
            if entity_name:
                query = query.filter(or_(Entity.entity_name_en.ilike(f"%{entity_name}%"), Entity.entity_name_ar.ilike(f"%{entity_name}%")))

            return query.all()
        except SQLAlchemyError as e:
            raise ServiceError(
                message=f"Failed to search entities: {str(e)}",
                name="Database Error"
            )

    def create_entity(self, entity_id: int, entity_name_en: str, entity_name_ar: str, entity_parent_id: int, entity_type_id: int) -> Entity:
        """Create a new entity."""
        try:
            entity = Entity(
                entity_id=entity_id,
                entity_name_en=entity_name_en,
                entity_name_ar=entity_name_ar,
                entity_parent_id=entity_parent_id,
                entity_type_id=entity_type_id
            )
            super().create(entity)
            return entity
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ServiceError(
                message=f"Failed to create entity: {str(e)}",
                name="Database Error"
            )
            
    def assign_member_to_entity(
        self, 
        entity_id: int,
        member_id: str, 
        role_id: int,
        from_date: Optional[str] = None
    ) -> EntityMember:
        """
        Assign member to entity with role.
        
        Args:
            entity_id: Entity identifier
            member_id: Member identifier
            role_id: Role identifier
            from_date: Start date of assignment (defaults to today)
            Returns:
                EntityMember: The created assignment record

            Raises:
                ServiceError: If assignment fails
        """
        logger.info(f"Assigning member {member_id} to entity {entity_id} with role {role_id}")
        try:
        
            # Create new assignment
            assignment = EntityMember(
                entity_id=entity_id,
                member_id=member_id,
                member_entity_role_id=role_id,
                date_from=from_date
            )
            
            self.db.add(assignment)
            self.db.commit()
            self.db.refresh(assignment)
            
            logger.info(f"Successfully assigned member {member_id} to entity {entity_id}")
            return assignment
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ServiceError(
                message=f"Failed to create entity: {str(e)}",
                name="Database Error"
            )
            
    def end_member_membership(self, entity_id: int, member_id: str, end_date: Optional[str] = None) -> None:
        """End a member's membership in an entity."""
        logger.info(f"Ending membership for member {member_id} in entity {entity_id}")
        try:
            # Find the existing active assignment
            assignment = (
                self.db.query(EntityMember)
                .filter(
                    and_(
                        EntityMember.entity_id == entity_id,
                        EntityMember.member_id == member_id,
                        EntityMember.date_to.is_(None)  # Active assignment
                    )
                )
                .first()
            )

            if not assignment:
                logger.warning(f"No active membership found for member {member_id} in entity {entity_id}.")
                raise EntityDoesNotExistError(
                    message=f"No active membership found for member {member_id} in entity {entity_id}.",
                    name="Entity Member Role Update Error"
                )

            # Update the end date
            assignment.date_to = end_date if end_date else datetime.now().date()
            self.db.commit()
            logger.info(f"Successfully ended membership for member {member_id} in entity {entity_id}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ServiceError(
                message=f"Failed to end member membership: {str(e)}",
                name="Database Error"
            )

    def update_entity(self, entity_id: int, entity_name_en: str, entity_name_ar: str, entity_parent_id: int, entity_type_id: int) -> Entity | None:
        """Update an existing entity."""
        try:
            entity = (
                self.db.query(Entity)
                .filter(Entity.entity_id == entity_id)
                .first()
            )
            entity.entity_name_en = entity_name_en
            entity.entity_name_ar = entity_name_ar
            entity.entity_parent_id = entity_parent_id
            entity.entity_type_id = entity_type_id

            
            return self.update(entity)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ServiceError(
                message=f"Failed to update entity: {str(e)}",
                name="Database Error"
            )
            
    def delete_entity(self, entity_id: int) -> None:
        """Delete an entity."""
        try:
            entity = self.get_entity_by_id(entity_id)

            self.delete(entity)
        
        except Exception as e:
            self.db.rollback()
            raise ServiceError(
                message=f"Failed to delete entity: {str(e)}",
                name="Database Error"
            )
