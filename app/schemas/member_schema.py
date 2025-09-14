from datetime import date
from typing import List, Optional

from pydantic import Field, field_validator

from app.schemas.base_schema import BaseSchema
from app.schemas.common_schema import NameObject

# Requests

class MemberRequest(BaseSchema):
    member_id: Optional[str] = Field(default=None,alias='MemberID', description="The unique identifier for the member (for creation only till ID generation is implemented)")
    name: Optional[NameObject] = Field(default=None,alias='Name', description="The name of the member")
    place_of_birth: Optional[str] = Field(default=None,alias='PlaceOfBirth', description="The place of birth of the member")
    date_of_birth: Optional[date] = Field(default=None,alias='DateOfBirth', description="The date of birth of the member")
    address: Optional[str] = Field(default=None,alias='Address', description="The address of the member")
    national_id_no: Optional[str] = Field(default=None,alias='NationalIdNo', description="The national ID number of the member")
    club_id_no: Optional[str] = Field(default=None,alias='ClubIdNo', description="The club ID number of the member")
    passport_no: Optional[str] = Field(default=None,alias='PassportNo', description="The passport number of the member")
    date_joined: Optional[int] = Field(default=None,alias='DateJoined', ge=2003, description="The date the member joined")
    mobile_number: Optional[str] = Field(default=None,alias='MobileNo', description="The mobile number of the member")
    home_contact: Optional[str] = Field(default=None,alias='HomeContact', description="The home contact number of the member")
    email: Optional[str] = Field(default=None,alias='Email', description="The email address of the member")
    facebook_url: Optional[str] = Field(default=None,alias='FacebookURL', description="The Facebook profile URL of the member")
    school_name: Optional[str] = Field(default=None,alias='SchoolName', description="The school name of the member")
    education_type: Optional[str] = Field(default=None,alias='EducationType', description="The education type of the member")
    father_name: Optional[str] = Field(default=None,alias='FatherName', description="The father's name of the member")
    father_contact: Optional[str] = Field(default=None,alias='FatherContact', description="The father's contact number of the member")
    father_job: Optional[str] = Field(default=None,alias='FatherJob', description="The father's job of the member")
    mother_name: Optional[str] = Field(default=None,alias='MotherName', description="The mother's name of the member")
    mother_contact: Optional[str] = Field(default=None,alias='MotherContact', description="The mother's contact number of the member")
    mother_job: Optional[str] = Field(default=None,alias='MotherJob', description="The mother's job of the member")
    guardian_name: Optional[str] = Field(default=None,alias='GuardianName', description="The guardian's name of the member")
    guardian_contact: Optional[str] = Field(default=None,alias='GuardianContact', description="The guardian's contact number of the member")
    guardian_relationship: Optional[str] = Field(default=None,alias='GuardianRelationship', description="The guardian's relationship to the member")
    hobbies: Optional[str] = Field(default=None,alias='Hobbies', description="The hobbies of the member")
    health_issues: Optional[str] = Field(default=None,alias='HealthIssues', description="The health issues of the member")
    medications: Optional[str] = Field(default=None,alias='Medications', description="The medications of the member")
    qr_code_url: Optional[str] = Field(default=None,alias='QRCodeURL', description="The QR code URL of the member")
    image_url: Optional[str] = Field(default=None,alias='ImageURL', description="The image URL of the member")
    national_id_url: Optional[str] = Field(default=None,alias='NationalIdURL', description="The national ID URL of the member")
    parent_national_id_url: Optional[str] = Field(default=None,alias='ParentNationalIdURL', description="The parent's national ID URL of the member")
    club_id_url: Optional[str] = Field(default=None,alias='ClubIdURL', description="The club ID URL of the member")
    passport_url: Optional[str] = Field(default=None,alias='PassportURL', description="The passport URL of the member")
    birth_certificate_url: Optional[str] = Field(default=None,alias='BirthCertificateURL', description="The birth certificate URL of the member")
    photo_consent: Optional[bool] = Field(default=None,alias='PhotoConsent', description="The photo consent status of the member")
    conditions_consent: Optional[bool] = Field(default=None,alias='ConditionsConsent', description="The conditions consent status of the member")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is None or v == '':
            return None
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v



# Responses
class Membership(BaseSchema):
    entity_id: int = Field(alias='EntityID')
    entity_name: NameObject = Field(alias='EntityName')
    role_id: int = Field(alias='RoleID', default=5)
    role_name: NameObject = Field(alias='RoleName')
    from_date: Optional[date] = Field(alias='FromDate')
    to_date: Optional[date] = Field(alias='ToDate')
    is_current_entity: bool = Field(alias='IsCurrentEntity')
    
    
class AttendanceState(BaseSchema):
        attendance_state_id: int = Field(alias='AttendanceStateID', description="The unique identifier for the attendance state")
        attendance_state_name: NameObject = Field(alias='AttendanceStateName', description="The name of the attendance state")
        
class MemberAttendance(BaseSchema):
    event_id: int = Field(alias='EventID', description="The unique identifier for the event")
    event_name: NameObject = Field(alias='EventName', description="The name of the event")
    attendance_state: AttendanceState = Field(alias='AttendanceState', description="The attendance status for the member in the event (e.g., Present, Absent, Excused, Late)")
    

class MemberResponse(BaseSchema):
    member_id: Optional[str] = Field(alias='MemberID', description="The unique identifier for the member")
    name: Optional[NameObject] = Field(alias='Name', description="The name of the member")
    place_of_birth: Optional[str] = Field(alias='PlaceOfBirth', description="The place of birth of the member")
    date_of_birth: Optional[date] = Field(alias='DateOfBirth', description="The date of birth of the member")
    address: Optional[str] = Field(alias='Address', description="The address of the member")
    national_id_no: Optional[str] = Field(alias='NationalIdNo', description="The national ID number of the member")
    club_id_no: Optional[str] = Field(alias='ClubIdNo', description="The club ID number of the member")
    passport_no: Optional[str] = Field(alias='PassportNo', description="The passport number of the member")
    date_joined: Optional[int] = Field(alias='DateJoined', ge=2003, description="The date the member joined")
    mobile_number: Optional[str] = Field(alias='MobileNo', description="The mobile number of the member")
    home_contact: Optional[str] = Field(alias='HomeContact', description="The home contact number of the member")
    email: Optional[str] = Field(alias='Email', description="The email address of the member")
    facebook_url: Optional[str] = Field(alias='FacebookURL', description="The Facebook profile URL of the member")
    school_name: Optional[str] = Field(alias='SchoolName', description="The school name of the member")
    education_type: Optional[str] = Field(alias='EducationType', description="The education type of the member")
    father_name: Optional[str] = Field(alias='FatherName', description="The father's name of the member")
    father_contact: Optional[str] = Field(alias='FatherContact', description="The father's contact number of the member")
    father_job: Optional[str] = Field(alias='FatherJob', description="The father's job of the member")
    mother_name: Optional[str] = Field(alias='MotherName', description="The mother's name of the member")
    mother_contact: Optional[str] = Field(alias='MotherContact', description="The mother's contact number of the member")
    mother_job: Optional[str] = Field(alias='MotherJob', description="The mother's job of the member")
    guardian_name: Optional[str] = Field(alias='GuardianName', description="The guardian's name of the member")
    guardian_contact: Optional[str] = Field(alias='GuardianContact', description="The guardian's contact number of the member")
    guardian_relationship: Optional[str] = Field(alias='GuardianRelationship', description="The guardian's relationship to the member")
    hobbies: Optional[str] = Field(alias='Hobbies', description="The hobbies of the member")
    health_issues: Optional[str] = Field(alias='HealthIssues', description="The health issues of the member")
    medications: Optional[str] = Field(alias='Medications', description="The medications of the member")
    qr_code_url: Optional[str] = Field(alias='QRCodeURL', description="The QR code URL of the member")
    image_url: Optional[str] = Field(alias='ImageURL', description="The image URL of the member")
    national_id_url: Optional[str] = Field(alias='NationalIdURL', description="The national ID URL of the member")
    parent_national_id_url: Optional[str] = Field(alias='ParentNationalIdURL', description="The parent's national ID URL of the member")
    club_id_url: Optional[str] = Field(alias='ClubIdURL', description="The club ID URL of the member")
    passport_url: Optional[str] = Field(alias='PassportURL', description="The passport URL of the member")
    birth_certificate_url: Optional[str] = Field(alias='BirthCertificateURL', description="The birth certificate URL of the member")
    photo_consent: Optional[bool] = Field(alias='PhotoConsent', description="The photo consent status of the member")
    conditions_consent: Optional[bool] = Field(alias='ConditionsConsent', description="The conditions consent status of the member")
    entities: Optional[List[Membership]] = Field(alias='Entities', description="The entities the member is part of")

    # @field_validator('email')
    # @classmethod
    # def validate_email(cls, v):
    #     if v is None or v == '':
    #         return None
    #     import re
    #     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    #     if not re.match(pattern, v):
    #         raise ValueError('Invalid email format')
    #     return v

class SearchMembersResponse(BaseSchema):
    members: List[MemberResponse] = Field(alias='Members')
    
class MemberAttendanceResponse(BaseSchema):
    total_events: int = Field(alias='TotalEvents', description="Total number of events the member was a part of")
    attended_events: int = Field(alias='AttendedEvents', description="Number of events the member attended (including being late)")
    attendance_percentage: float = Field(alias='AttendancePercentage', description="Attendance percentage of the member (including being late)")
    absent_percentage: float = Field(alias='AbsentPercentage', description="Absent percentage of the member")
    excused_percentage: float = Field(alias='ExcusedPercentage', description="Excused percentage of the member")
    late_percentage: float = Field(alias='LatePercentage', description="Late percentage of the member")
    member_attendance: List[MemberAttendance] = Field(alias='MemberAttendance', description="List of attendance records for the member")