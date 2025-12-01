from datetime import datetime
from typing import List, Optional

from pydantic import Field

from app.schemas.base_schema import BaseSchema


# Requests
class PermissionCreate(BaseSchema):
    name: str = Field(alias="Name")
    display_name: str = Field(alias="DisplayName")
    description: Optional[str] = Field(alias="Description", default=None)
    category: str = Field(alias="Category")
    # is_active: bool = Field(alias="IsActive", default=True)
    
class PermissionUpdate(BaseSchema):
    name: str = Field(alias="Name")
    display_name: str = Field(alias="DisplayName")
    description: Optional[str] = Field(alias="Description", default=None)
    category: str = Field(alias="Category")
    is_active: bool = Field(alias="IsActive", default=True)
    
# Responses
class PermissionResponse(BaseSchema):
    id: int = Field(alias="ID")
    name: str = Field(alias="Name")
    display_name: str = Field(alias="DisplayName")
    description: Optional[str] = Field(alias="Description", default=None)
    category: str = Field(alias="Category")
    is_active: bool = Field(alias="IsActive")
    created_at: datetime = Field(alias="CreatedAt")
    updated_at: Optional[datetime] = Field(alias="UpdatedAt")
    
class PermissionListResponse(BaseSchema):
    permissions: List[PermissionResponse] = Field(alias="Permissions")