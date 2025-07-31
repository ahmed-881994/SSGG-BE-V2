from pydantic import BaseModel, Field


class AddEntityMemberRequest(BaseModel):
    member_id: int = Field(..., description="The ID of the member to add", alias='MemberID')
    role: int = Field(5, description="The role of the member (default is 5)", alias='Role')
    from_date: str = Field(..., description="The date from which the member is added", alias='FromDate')
