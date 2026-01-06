from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql import text

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
        self.join_stage_codes = {
            'Smurfs/Pres': 1,
            'Cubs/Jeanette': 2,
            'Scout/Guide': 3,
            'Senior/GA': 4,
            'Rover': 5,
            'Leader': 6}

    def _transform_name_fields(self, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform name fields to separate English and Arabic names."""
        member_data['name_en'] = member_data.get('name', {}).get('en', '').strip()
        member_data['name_ar'] = member_data.get('name', {}).get('ar', '').strip()
        member_data.pop('name', None)
        return member_data
    
    def _generate_member_id(self, stage_joined: str, join_year: int, birth_year: str, gender: str) -> str:
        
        serial_number_query = self.db_session.query(Member).filter(Member.date_joined == join_year)
        serial_number = serial_number_query.count() + 1
        
        group_letter = 'S' if gender.lower() == 'male' else 'G'
        stage_joined_char = self.join_stage_codes.get(stage_joined)
        join_year_chars = str(join_year)[-2:]
        birth_year_chars = birth_year[-2:]
        serial_number_chars = str(serial_number).zfill(3)
        
        return f"{group_letter}{stage_joined_char}{join_year_chars}{birth_year_chars}{serial_number_chars}"
        
        

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
            member_id = member_data.get('member_id')
            if member_id:
                member = self.member_repository.get_member_by_member_id(member_id)
                # If member with provided member_id already exists, raise error
                if member:
                    raise EntityAlreadyExistsError("Member with this ID already exists.", name="Member Creation Error")

            # Generate member_id if not provided
            else:
                member_data['member_id'] = self._generate_member_id(
                    stage_joined=member_data.get('stage_joined', ''),
                    join_year=member_data.get('date_joined', 2003),
                    birth_year=str(member_data.get('date_of_birth', 0))[:4],
                    gender=member_data.get('gender', '')
                )
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
                message=f"Failed to create member",
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
                message=f"Failed to update member",
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
                message=f"Failed to delete member",
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
                        "event_start_date": attendance.event.event_start_date,
                        "event_end_date": attendance.event.event_end_date,
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
                message=f"Failed to retrieve member attendance",
                name="Member Attendance Retrieval Error"
            )