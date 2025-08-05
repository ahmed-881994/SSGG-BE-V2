from typing import Optional

from pydantic import BaseModel, Field

from app.schema.common import Entity, Name


class SearchEntitiesResponse(BaseModel):
    entity_id: int = Field(alias="EntityID", description="The ID of the entity.")
    entity_name: Name = Field(alias="EntityName", description="The name of the entity.")
    parent: Optional[Entity] = Field(None, alias="Parent", description="The parent of the entity.")
    children: Optional[list[Entity]] = Field(None, alias="Children", description="List of child entities.")