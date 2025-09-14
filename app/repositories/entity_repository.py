from datetime import date, datetime
from logging import getLogger
from typing import List, Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import EntityDoesNotExistError, ServiceError
from app.models.entity_member_model import EntityMember
from app.models.entity_model import Entity
from app.models.entity_role_model import EntityRole
from app.repositories.base_repository import BaseRepository

logger = getLogger(__name__)

class EntityRepository(BaseRepository[Entity]):
    """Repository for Entity database operations."""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, Entity)
        
    def member_exists(self, member_id: str) -> bool:
        """Check if a member exists."""
        return self.db.query(EntityMember).filter(EntityMember.member_id == member_id).first() is not None
    
    def get_active_member_assignment(self, entity_id: int, member_id: str, role_id: Optional[int] = None) -> Optional[EntityMember]:
        """Get active assignment for a member in an entity, optionally filtered by role."""
        query = self.db.query(EntityMember).filter(
            and_(
                EntityMember.entity_id == entity_id,
                EntityMember.member_id == member_id,
                EntityMember.date_to.is_(None)
            )
        )
        
        if role_id:
            query = query.filter(EntityMember.member_entity_role_id == role_id)
        
        return query.first()

    def role_exists(self, role_id: int) -> bool:
        """Check if an entity role exists."""
        return self.db.query(EntityRole).filter(EntityRole.entity_role_id == role_id).first() is not None
    
    
    def update_member_assignment_end_date(self, assignment: EntityMember, end_date) -> None:
        """Update the end date of a member assignment."""
        assignment.date_to = end_date
        self.db.commit()
        self.db.refresh(assignment)
        
    def update_member_role(self, entity_id: int, member_id: str, new_role_id: int) -> bool:
        """Update the role of an active member in an entity."""
        assignment = self.get_active_member_assignment(entity_id, member_id)
        if assignment:
            assignment.member_entity_role_id = new_role_id
            self.db.commit()
            self.db.refresh(assignment)
            return True
        return False

    def delete_entity_members(self, entity_id: int) -> None:
        """Delete all entity members for a given entity. (consider soft delete e.g. setting a 'deleted' flag or setting date_to)"""
        self.db.query(EntityMember).filter(EntityMember.entity_id == entity_id).delete()
        self.db.commit()

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
            entity = self.db.query(Entity).filter(Entity.entity_id == entity_id).first()
            if entity:
                # Access members through the relationship
                members = entity.entity_members  # This will lazy load the members
                # Apply filters
                filtered_members = members
                
                if not include_inactive:
                    # Filter out inactive members
                    filtered_members = [member for member in filtered_members if member.date_to is None]
                    
                if role_id:
                    # Filter by role
                    filtered_members = [member for member in filtered_members if member.member_entity_role_id == role_id]

                return filtered_members
            return []
        except SQLAlchemyError as e:
            raise ServiceError(
                message=f"Failed to retrieve entity members: {str(e)}",
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
            entity = Entity()
            entity.entity_id = entity_id
            entity.entity_name_en = entity_name_en
            entity.entity_name_ar = entity_name_ar
            entity.entity_parent_id = entity_parent_id
            entity.entity_type_id = entity_type_id
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
        from_date: Optional[date] = None
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
            assignment = EntityMember()
            assignment.entity_id = entity_id
            assignment.member_id = member_id
            assignment.member_entity_role_id = role_id
            assignment.date_from = from_date

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
            
    def delete_entity(self, entity_id: int) -> bool:
        """Delete an entity."""
        try:
            entity = self.get_entity_by_id(entity_id)

            return super().delete(entity)

        except Exception as e:
            self.db.rollback()
            raise ServiceError(
                message=f"Failed to delete entity: {str(e)}",
                name="Database Error"
            )
