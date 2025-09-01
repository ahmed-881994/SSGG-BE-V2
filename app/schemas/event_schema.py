from datetime import date
from typing import Optional

from pydantic import Field, field_validator

from app.schemas.base_schema import BaseSchema
from app.schemas.common_schema import NameObject

# Types

class EventType(BaseSchema):
    event_type_id: int = Field(alias="EventTypeID")
    event_type_name: NameObject = Field(alias="EventTypeName")

class EventEntity(BaseSchema):
    entity_id: int = Field(alias="EntityID")
    entity_name: NameObject = Field(alias="EntityName")

class AttendanceState(BaseSchema):
    attendance_state_id: int = Field(alias="AttendanceStateID")
    attendance_state_name: NameObject = Field(alias="AttendanceStateName")

class AttendanceRecord(BaseSchema):
    member_id: str = Field(alias="MemberID")
    member_name: NameObject = Field(alias="MemberName")
    attendance_state: AttendanceState = Field(alias="AttendanceState")
    
class AttendanceUpdateRecord(BaseSchema):
    member_id: str = Field(alias="MemberID")
    attendance_state_id: int = Field(alias="AttendanceStateID")

# Requests
class EventCreate(BaseSchema):
    event_name: NameObject = Field(alias="EventName")
    event_start_date: date = Field(alias="EventStartDate")
    event_end_date: Optional[date] = Field(default=None,alias="EventEndDate")
    event_location: Optional[str] = Field(default=None,alias="EventLocation")
    is_multi_team: bool = Field(alias="IsMultiTeam")
    event_type_id: int = Field(alias="EventTypeID")
    organizing_entity_id: int = Field(alias="OrganizingEntityID")
    participating_entities_ids: Optional[list[int]] = Field(default=None, alias="ParticipatingEntitiesIDs")

    @field_validator('participating_entities_ids')
    @classmethod
    def validate_participating_entities_ids(cls, v):
        if v is None:
            return None
        return v
    
class EventUpdate(BaseSchema):
    event_name: Optional[NameObject] = Field(default=None, alias="EventName")
    event_start_date: Optional[date] = Field(default=None, alias="EventStartDate")
    event_end_date: Optional[date] = Field(default=None, alias="EventEndDate")
    event_location: Optional[str] = Field(default=None, alias="EventLocation")
    is_multi_team: Optional[bool] = Field(default=None, alias="IsMultiTeam")
    event_type_id: Optional[int] = Field(default=None, alias="EventTypeID")
    organizing_entity_id: Optional[int] = Field(default=None, alias="OrganizingEntityID")
    participating_entities_ids: Optional[list[int]] = Field(default=None, alias="ParticipatingEntitiesIDs")

    @field_validator('participating_entities_ids')
    @classmethod
    def validate_participating_entities_ids(cls, v):
        if v is None:
            return None
        return v
    
class EventAttendanceUpdate(BaseSchema):
    attendance: list[AttendanceUpdateRecord] = Field(alias="Attendance")


# Responses
class EventResponse(BaseSchema):
    event_id: int = Field(alias="EventID")
    event_name: NameObject = Field(alias="EventName")
    event_start_date: date = Field(alias="EventStartDate")
    event_end_date: Optional[date] = Field(alias="EventEndDate")
    event_location: Optional[str] = Field(alias="EventLocation")
    is_multi_team: bool = Field(alias="IsMultiTeam")
    event_type: EventType = Field(alias="EventType")
    organizing_entity: EventEntity = Field(alias="OrganizingEntity")
    participating_entities: Optional[list[EventEntity]] = Field(alias="ParticipatingEntities")


class SearchEventsResponse(BaseSchema):
    events: list[EventResponse] = Field(alias="Events")
    
    
class EventAttendanceResponse(BaseSchema):
    event_id: int = Field(alias="EventID")
    event_name: NameObject = Field(alias="EventName")
    attendance_records: list[AttendanceRecord] = Field(alias="AttendanceRecords")

