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
            member = Member()
            member.member_id = member_data.get("member_id")
            member.name_en = member_data.get("name_en")
            member.name_ar = member_data.get("name_ar")
            member.place_of_birth = member_data.get("place_of_birth")
            member.date_of_birth = member_data.get("date_of_birth")
            member.address = member_data.get("address")
            member.national_id_no = member_data.get("national_id_no")
            member.club_id_no = member_data.get("club_id_no")
            member.passport_no = member_data.get("passport_no")
            member.date_joined = member_data.get("date_joined")
            member.mobile_number = member_data.get("mobile_number")
            member.home_contact = member_data.get("home_contact")
            member.email = member_data.get("email")
            member.facebook_url = member_data.get("facebook_url")
            member.school_name = member_data.get("school_name")
            member.education_type = member_data.get("education_type")
            member.father_name = member_data.get("father_name")
            member.father_contact = member_data.get("father_contact")
            member.father_job = member_data.get("father_job")
            member.mother_name = member_data.get("mother_name")
            member.mother_contact = member_data.get("mother_contact")
            member.mother_job = member_data.get("mother_job")
            member.guardian_name = member_data.get("guardian_name")
            member.guardian_contact = member_data.get("guardian_contact")
            member.guardian_relationship = member_data.get("guardian_relationship")
            member.hobbies = member_data.get("hobbies")
            member.health_issues = member_data.get("health_issues")
            member.medications = member_data.get("medications")
            member.qr_code_url = member_data.get("qr_code_url")
            member.image_url = member_data.get("image_url")
            member.national_id_url = member_data.get("national_id_url")
            member.parent_national_id_url = member_data.get("parent_national_id_url")
            member.club_id_url = member_data.get("club_id_url")
            member.passport_url = member_data.get("passport_url")
            member.birth_certificate_url = member_data.get("birth_certificate_url")
            member.photo_consent = member_data.get("photo_consent")
            member.conditions_consent = member_data.get("conditions_consent")
            
            
            
            
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