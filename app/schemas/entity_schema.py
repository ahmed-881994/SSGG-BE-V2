from typing import List, Optional

from pydantic import Field

from app.schemas.base_schema import BaseSchema
from app.schemas.common_schema import NameObject

# Requests

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
    
class Membership(BaseSchema):
    member_id: str = Field(alias='MemberID')
    role_id: Optional[int] = Field(alias='RoleID', default=5)
    from_date: str = Field(alias='FromDate')

class EntityAssign(BaseSchema):

    memberships: List[Membership] = Field(alias='Memberships')


class RoleUpdate(BaseSchema):
    member_id: str = Field(alias='MemberID')
    role_id: int = Field(alias='RoleID')


# Responses

class EntityTypeResponse(BaseSchema):
    """Schema for entity type data in responses."""
    entity_type_id: int = Field(alias='EntityTypeID')
    entity_type_name: NameObject = Field(alias='EntityTypeName')


class EntityResponse(BaseSchema):
    """Schema for entity data in responses."""
    entity_id: int = Field(alias='EntityID')
    entity_name: NameObject = Field(alias='EntityName')
    entity_parent_id: Optional[int] = Field(alias='EntityParentID', default=None)
    entity_type: EntityTypeResponse = Field(alias='EntityType')


class EntitySearchResponse(BaseSchema):
    """Schema for list of entities response."""
    entities: List[EntityResponse] = Field(alias='Entities')

class EntityMemberResponse(BaseSchema):
    """Schema for individual entity member response."""
    member_id: str = Field(alias='MemberID')
    member_name: NameObject = Field(alias='MemberName')
    role_id: int = Field(alias='RoleID')
    role_name: NameObject = Field(alias='RoleName')
    date_from: str = Field(alias='DateFrom')
    date_to: Optional[str] = Field(alias='DateTo', default=None)
    is_active: bool = Field(alias='IsActive')


class EntityMembersResponse(BaseSchema):
    """Schema for the complete entity members response."""
    members: List[EntityMemberResponse] = Field(alias='Members')
    
class EntityHierarchicalResponse(EntityResponse):
    """Schema for entity with hierarchical relationships (children and parent)."""
    children: Optional[List[EntityResponse]] = Field(alias='Children', default=None)
    parent: Optional[EntityResponse] = Field(alias='Parent', default=None)