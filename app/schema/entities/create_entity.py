from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

class EntityType(int, Enum):
    Team = 1
    Stage = 2
    AgeGroup = 3
    GenderGroup = 4

class CreateEntityRequest(BaseModel):
    entity_type: EntityType = Field(..., alias="EntityType", description="The type of the entity (e.g., 'stage', 'ageGroup').")
    entity_id: int = Field(..., alias="EntityID", description="The ID of the entity.")
    member_id: str = Field(..., alias="MemberID", description="The ID of the member to assign.")
    role_id: int = Field(..., alias="RoleID", description="The role ID to assign to the member.")
