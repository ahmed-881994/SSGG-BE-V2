from typing import Dict, List

from pydantic import Field

from app.schemas.base_schema import BaseSchema


# Requests
class VisualizerQuery(BaseSchema):
    query: str = Field(alias="Query")
    
# Responses
class VisualizerQueryResponse(BaseSchema):
    columns: List[str] = Field(alias="Columns")
    rows: List[Dict] = Field(alias="Rows")