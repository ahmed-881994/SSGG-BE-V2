from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError, ServiceError
from app.models.member import Member
from app.repositories.base_repository import BaseRepository


class MemberRepository(BaseRepository[Member]):
    """Repository for EntityMember database operations."""

    def __init__(self, db_session: Session):
        super().__init__(db_session, Member)
        
    def get_member_by_id(self, member_id: int) -> Member | None:
        """Get a member by ID."""
        try:
            return self.db.query(Member).filter(Member.member_id == member_id).one_or_none()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ServiceError(message=str(e), name="Database Error")