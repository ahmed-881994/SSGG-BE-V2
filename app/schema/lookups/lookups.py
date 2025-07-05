from pydantic import BaseModel, Field


class LookupValues(BaseModel):
    lookup_id: int = Field(alias='LookupID', default=None)
    ar: str = Field(alias='AR', default=None)
    en: str = Field(alias='EN', default=None)


class Lookup(BaseModel):
    table_name: str = Field(alias='TableName', default=None)
    description: str = Field(alias='Description', default=None)
    lookup_values: list[LookupValues] = Field(alias='LookupValues', default=None)
    
    
