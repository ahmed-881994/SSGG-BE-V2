from typing import Optional
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    detail: str
    
class SuccessResponse(BaseModel):
    message: str
    
class Name(BaseModel):
    en: Optional[str] = Field(alias='EN', default="")
    ar: Optional[str] = Field(alias='AR', default="")
    
class MemberBrief(BaseModel):
        member_id: str = Field(alias='MemberID')
        name: Name = Field(alias='Name')
        
class AttendanceItem(BaseModel):
        member: MemberBrief = Field( alias='Member')
        attendance_id: int = Field(alias='AttendanceID')
        attendance_state_id: int = Field(alias='AttendanceStateID')
        attendance_state_name: Name = Field(alias='AttendanceStateName')