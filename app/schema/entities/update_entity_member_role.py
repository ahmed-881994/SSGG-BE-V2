from pydantic import BaseModel, Field


class UpdateEntityMemberRoleRequest(BaseModel):
    """
    Request schema for updating member roles in an entity.
    """
    member_id: str = Field(alias='MemberID')
    role: str = Field(alias='Role')