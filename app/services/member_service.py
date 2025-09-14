from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.exceptions import (EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.models.member_model import Member
from app.repositories.member_repository import MemberRepository


class MemberService:
    """Service for Member operations."""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.member_repository = MemberRepository(db_session)


    def _transform_name_fields(self, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform name fields to separate English and Arabic names."""
        member_data['name_en'] = member_data.get('name', {}).get('en', '').strip()
        member_data['name_ar'] = member_data.get('name', {}).get('ar', '').strip()
        member_data.pop('name', None)
        return member_data

    def format_member_data(self, member: Member) -> Dict[str, Any]:
        """Format member data to include entities and roles."""
        member_dict = member.to_dict()
        entities = []
        for em in member.entity_memberships:
            entity_dict = {
                "entity_id": em.entity.entity_id if em.entity else None,
                "entity_name": {
                    "en": em.entity.entity_name_en if em.entity else None,
                    "ar": em.entity.entity_name_ar if em.entity else None
                },
                "role_id": em.member_entity_role_id,
                "role_name": {
                    "en": em.role.entity_role_name_en if em.role else None,
                    "ar": em.role.entity_role_name_ar if em.role else None
                },
                "from_date": em.date_from.isoformat() if em.date_from else None,
                "to_date": em.date_to.isoformat() if em.date_to else None,
                "is_current_entity": em.date_to is None
            }
            entities.append(entity_dict)
        member_dict["entities"] = entities
        return member_dict

    def get_member_by_member_id(self, member_id: str) -> Dict[str, Any]:
        try:
            member = self.member_repository.get_member_by_member_id(member_id)
            if not member:
                raise EntityDoesNotExistError(f"Member with ID {member_id} does not exist.", name="Member Retrieval Error")
            return self.format_member_data(member)
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving member: {member_id}: {str(e)}")
            raise ServiceError(
                message=f"Failed to retrieve member: {str(e)}",
                name="Member Retrieval Error"
            )

    def search_members(self, name: Optional[str] = None, entity_id: Optional[int] = None) -> Dict[str,List[Dict[str, Any]]]:
        try:
            members = self.member_repository.search_members(name=name, entity_id=entity_id)
            if not members:
                raise EntityDoesNotExistError("No members found matching the criteria.", name="Member Search Error")
            result = {"members": []}
            for member in members:
                result["members"].append(self.format_member_data(member))
            return result
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error searching members: {str(e)}")
            raise ServiceError(
                message=f"Failed to search members: {str(e)}",
                name="Member Search Error"
            )
            
    def create_member(self, member_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            member = self.member_repository.get_member_by_member_id(member_data.get('member_id'))
            if member:
                raise EntityAlreadyExistsError("Member with this ID already exists.", name="Member Creation Error")

            # TODO Generate member_id if not provided
            
            # format member_data as needed
            member_data = self._transform_name_fields(member_data)
            # If member does not exist, create a new record
            member = self.member_repository.create_member(member_data)
            return self.format_member_data(member)
        except EntityAlreadyExistsError:
            raise
        except Exception as e:
            logger.error(f"Error creating member: {str(e)}")
            raise ServiceError(
                message=f"Failed to create member: {str(e)}",
                name="Member Creation Error"
            )
            
    def update_member(self, member_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            member = self.member_repository.get_member_by_member_id(member_id)
            if not member:
                raise EntityDoesNotExistError("Member not found", name="Member Update Error")

            # format member_data as needed
            update_data = self._transform_name_fields(update_data)

            member = self.member_repository.update_member(member_id, update_data)
            return self.format_member_data(member)
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error updating member: {str(e)}")
            raise ServiceError(
                message=f"Failed to update member: {str(e)}",
                name="Member Update Error"
            )
            
    def delete_member(self, member_id: str) -> None:
        try:
            member = self.member_repository.get_member_by_member_id(member_id)
            if not member:
                raise EntityDoesNotExistError("Member not found", name="Member Deletion Error")
            self.member_repository.delete_member(member_id)
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error deleting member: {str(e)}")
            raise ServiceError(
                message=f"Failed to delete member: {str(e)}",
                name="Member Deletion Error"
            )

    def get_member_attendance(self, member_id: str) -> Dict[str, List[Dict[str, Any]]]:
        try:
            member = self.member_repository.get_member_by_member_id(member_id)
            if not member:
                raise EntityDoesNotExistError(f"Member with ID {member_id} does not exist.", name="Member Retrieval Error")
            member_attendance = {
                "member_attendance": [
                    {
                        "event_id": attendance.event.event_id,
                        "event_name": {
                            "en": attendance.event.event_name_en,
                            "ar": attendance.event.event_name_ar
                        },
                        "attendance_state": {
                            "attendance_state_id": attendance.attendance_state_id,
                            "attendance_state_name": {
                            "en": attendance.attendance_state.attendance_state_name_en,
                            "ar": attendance.attendance_state.attendance_state_name_ar
                        }
                    },
                    
                }
                for attendance in member.attendance_records
            ],
                "total_events": len(member.attendance_records),
                "attended_events": sum(1 for attendance in member.attendance_records if attendance.attendance_state_id == 1 or attendance.attendance_state_id == 4),
                "attendance_percentage": (sum(1 for attendance in member.attendance_records if attendance.attendance_state_id == 1 or attendance.attendance_state_id == 4) / len(member.attendance_records) * 100) if member.attendance_records else 0.0,
                "absent_percentage": (sum(1 for attendance in member.attendance_records if attendance.attendance_state_id == 2) / len(member.attendance_records) * 100) if member.attendance_records else 0.0,  
                "excused_percentage": (sum(1 for attendance in member.attendance_records if attendance.attendance_state_id == 3) / len(member.attendance_records) * 100) if member.attendance_records else 0.0,
                "late_percentage": (sum(1 for attendance in member.attendance_records if attendance.attendance_state_id == 4) / len(member.attendance_records) * 100) if member.attendance_records else 0.0 
            }
            return member_attendance
        except EntityDoesNotExistError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving attendance for member {member_id}: {str(e)}")
            raise ServiceError(
                message=f"Failed to retrieve member attendance: {str(e)}",
                name="Member Attendance Retrieval Error"
            )