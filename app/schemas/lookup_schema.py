from typing import Optional

from pydantic import Field

from app.schemas.base_schema import BaseSchema


class LookupEntrySchema(BaseSchema):
    """Schema for individual lookup entries."""
    lookup_id: int = Field(alias="LookupID")
    en: str = Field(alias="EN")
    ar: Optional[str] = Field(alias="AR")

class LookupObjectSchema(BaseSchema):
    """Schema for Lookup table."""
    table_name: str = Field(alias="TableName")
    description: str = Field(alias="Description")
    lookup_values: list[LookupEntrySchema] = Field(alias="LookupValues")


class LookupResponseSchema(BaseSchema):
    """Schema for the overall lookup response."""
    lookups: list[LookupObjectSchema] = Field(alias="Lookups")