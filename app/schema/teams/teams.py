from typing import List, Optional

from pydantic import BaseModel, Field

from app.schema.common import AttendanceItem, MemberBrief, Name

    

class Team(BaseModel):
    

    class Stage(BaseModel):
        stage_id: Optional[int] = Field(None, alias='StageID')
        name: Optional[Name] = Field(None, alias='Name')

    team_id: Optional[int] = Field(None, alias='TeamID')
    name: Optional[Name] = Field(None, alias='Name')
    stage: Optional[Stage] = Field(None, alias='Stage')
    leaders: Optional[List[MemberBrief]] = Field(None, alias='Leaders')
    members: Optional[List[MemberBrief]] = Field(None, alias='Members')

class TeamTransfer(BaseModel):
    class Member(BaseModel):
        member_id: str = Field(alias='MemberID')
        is_leader: int = Field(alias='IsLeader')
        
    from_team_id: int = Field(alias='FromTeamID')
    to_team_id: int = Field(alias='ToTeamID')
    transfer_date: str = Field(alias='TransferDate')
    member: Member = Field(alias='Member')
    
class TeamAttendance(BaseModel):

    event_id: Optional[int] = Field(None, alias='EventID')
    name: Name = Field(alias='Name')
    event_start_date: Optional[str] = Field(None, alias='EventStartDate')
    event_end_date: Optional[str] = Field(None, alias='EventEndDate')
    event_type_id: Optional[int] = Field(None, alias='EventTypeID')
    event_type_name_en: Optional[str] = Field(None, alias='EventTypeNameEN')
    event_type_name_ar: Optional[str] = Field(None, alias='EventTypeNameAR')
    attendance: Optional[List[AttendanceItem]] = Field(None, alias='Attendance')
    
class TeamAdd(BaseModel):
    member_id: str = Field(alias='MemberID')
    is_leader: bool = Field(alias='IsLeader')
    from_date: str = Field(alias='FromDate')