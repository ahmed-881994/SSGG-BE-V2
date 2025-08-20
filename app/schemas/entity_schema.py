from typing import Optional

from pydantic import Field

from app.schemas.base_schema import BaseSchema
from app.schemas.common_schema import NameObject

class EntityCreate(BaseSchema):
    entity_type: int = Field(alias='EntityType')
    entity_name: NameObject = Field(alias='EntityName')
    parent_id: Optional[int] = Field(alias='ParentID', default=None)

class EntityTransfer(BaseSchema):
    member_id: str = Field(alias='MemberID')
    from_entity_id: int = Field(alias='FromEntityID')
    to_entity_id: int = Field(alias='ToEntityID')
    role_id: Optional[int] = Field(alias='RoleID', default=5)
    transfer_date: str = Field(alias='TransferDate')


class RoleUpdate(BaseSchema):
    member_id: str = Field(alias='MemberID')
    role_id: int = Field(alias='RoleID')
