from typing import Any, Dict, List, Optional

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import ServiceError
from app.models.member_model import Member
from app.repositories.base_repository import BaseRepository


class MemberRepository(BaseRepository[Member]):
    """Repository for EntityMember database operations."""

    def __init__(self, db_session: Session):
        super().__init__(db_session, Member)
        
    def member_exists(self, member_id: str) -> bool:
        """Check if a member exists."""
        return self.db.query(Member).filter(Member.member_id == member_id).first() is not None
    
    def get_member_by_member_id(self, member_id: str) -> Member | None:
        """Get a member by ID."""
        try:
            return self.db.query(Member).filter(Member.member_id == member_id).one_or_none()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ServiceError(message=str(e), name="Database Error")
        
    def search_members(self, name: Optional[str] = None, entity_id: Optional[int] = None) -> List[Member]:
        """Search for members by name or entity ID."""
        try:
            query = self.db.query(Member)
            if name:
                query = query.filter(or_(Member.name_en.ilike(f"%{name}%"), Member.name_ar.ilike(f"%{name}%")))
            if entity_id:
                query = query.filter(Member.entity_memberships.any(entity_id=entity_id))
            return query.all()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ServiceError(message=str(e), name="Database Error")
        
    def create_member(self, member_data: Dict[str, Any]) -> Member:
        """Create new member with validation."""

        try:
            # Create member instance
            member = Member(**member_data)
            
            # Use base repository create method
            return super().create(member)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ServiceError(
                message=f"Failed to create entity: {str(e)}",
                name="Database Error"
            )
            
    def update_member(self, member_id: str, update_data: Dict[str, Any]) -> Member:
        """Update an existing member."""
        try:
            member = self.get_member_by_member_id(member_id)

            for key, value in update_data.items():
                setattr(member, key, value)

            super().update(member)
            return member
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ServiceError(message=str(e), name="Database Error")

    def delete_member(self, member_id: str) -> None:
        """Delete a member."""
        try:
            member = self.get_member_by_member_id(member_id)

            super().delete(member)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ServiceError(message=str(e), name="Database Error")