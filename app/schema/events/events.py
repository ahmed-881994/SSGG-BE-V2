from typing import List, Optional
from pydantic import BaseModel, Field

from app.schema.common import AttendanceItem, MemberBrief, Name

class Event(BaseModel):
    event_id: int = Field(alias='EventID')
    event_type_id: int = Field(alias='EventTypeID')
    name: Name = Field(alias='Name')
    location: Optional[str] = Field(None, alias='Location')
    start_date: str = Field(alias='StartDate')
    end_date: Optional[str] = Field(None, alias='EndDate')
    is_multi_team: Optional[bool] = Field(None, alias='IsMultiTeam')
    team_id: int = Field(alias='TeamID')
    
class EventCreate(BaseModel):
    event_type_id: int = Field(alias='EventTypeID')
    name: Name = Field(alias='Name')
    location: Optional[str] = Field(None, alias='Location')
    start_date: str = Field(alias='StartDate')
    end_date: Optional[str] = Field(None, alias='EndDate')
    is_multi_team: Optional[bool] = Field(None, alias='IsMultiTeam')
    team_id: int = Field(alias='TeamID')
    
class EventUpdate(BaseModel):
    event_type_id: Optional[int] = Field(None, alias='EventTypeID')
    name: Optional[Name] = Field(None, alias='Name')
    location: Optional[str] = Field(None, alias='Location')
    start_date: Optional[str] = Field(None, alias='StartDate')
    end_date: Optional[str] = Field(None, alias='EndDate')
    is_multi_team: Optional[bool] = Field(None, alias='IsMultiTeam')
    team_id: Optional[int] = Field(None, alias='TeamID')
    


class EventAttendance(BaseModel):
    
    event_id: int = Field(alias='EventID')
    attendance: List[AttendanceItem] = Field(alias='Attendance')


class UpdateEventAttendance(BaseModel):
    class UpdateEventAttendanceItem(BaseModel):
        member_id: str = Field(alias='MemberID')
        attendance_state_id: int = Field(alias='AttendanceStateID')
    attendance: List[UpdateEventAttendanceItem] = Field(alias='Attendance')