from typing import Optional
from pydantic import BaseModel, Field

from app.schema.common import Name


class CreateEntityRequest(BaseModel):
    entity_type: int = Field(..., alias="EntityType", gt=0, lt=5, description="The type of the entity (1.Team, 2.Stage, 3.AgeGroup, 4.GenderGroup).")
    entity_name: Name = Field(..., alias="EntityName", description="The name of the entity.")
    parent_id: Optional[int] = Field(None, alias="ParentID", description="The parent ID to assign to the entity.")
