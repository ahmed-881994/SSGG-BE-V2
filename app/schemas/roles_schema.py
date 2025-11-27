from datetime import datetime
from typing import List, Optional

from pydantic import Field

from app.schemas.base_schema import BaseSchema


class Permission(BaseSchema):
    id: int = Field(alias="ID")
    name: str = Field(alias="Name")
    display_name: str = Field(alias="DisplayName")
    description: Optional[str] = Field(alias="Description", default=None)
    category: bool = Field(alias="Category")
    is_active: bool = Field(alias="IsActive")
    created_at: datetime = Field(alias="CreatedAt")
    updated_at: Optional[datetime] = Field(alias="UpdatedAt")

# Requests
class RoleCreate(BaseSchema):
    name: str = Field(alias="Name")
    display_name: str = Field(alias="DisplayName")
    description: Optional[str] = Field(alias="Description", default=None)
    is_system_role: bool = Field(alias="IsSystemRole", default=False)
    # is_active: bool = Field(alias="IsActive", default=True)
    
class RoleUpdate(BaseSchema):
    name: Optional[str] = Field(alias="Name")
    display_name: Optional[str] = Field(alias="DisplayName")
    description: Optional[str] = Field(alias="Description")
    is_system_role: Optional[bool] = Field(alias="IsSystemRole")
    is_active: Optional[bool] = Field(alias="IsActive")
    
    
# Responses
class RoleResponse(BaseSchema):
    id: int = Field(alias="ID")
    name: str = Field(alias="Name")
    display_name: str = Field(alias="DisplayName")
    description: Optional[str] = Field(alias="Description", default=None)
    is_system_role: bool = Field(alias="IsSystemRole")
    is_active: bool = Field(alias="IsActive")
    created_at: datetime = Field(alias="CreatedAt")
    updated_at: Optional[datetime] = Field(alias="UpdatedAt")
    permissions: Optional[List[Permission]] = Field(alias="Permissions")

class RoleNoPermissionsResponse(BaseSchema):
    id: int = Field(alias="ID")
    name: str = Field(alias="Name")
    display_name: str = Field(alias="DisplayName")
    description: Optional[str] = Field(alias="Description", default=None)
    is_system_role: bool = Field(alias="IsSystemRole")
    is_active: bool = Field(alias="IsActive")
    created_at: datetime = Field(alias="CreatedAt")
    updated_at: Optional[datetime] = Field(alias="UpdatedAt")
    # permissions: Optional[List[Permission]] = Field(alias="Permissions")
    
class RoleSearchResponse(BaseSchema):
    roles: List[RoleNoPermissionsResponse] = Field(alias="Roles")
