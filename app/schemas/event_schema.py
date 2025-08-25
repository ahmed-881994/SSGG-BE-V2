from datetime import date
from typing import Optional

from pydantic import Field

from app.schemas.base_schema import BaseSchema
from app.schemas.common_schema import NameObject

# Types

class EventType(BaseSchema):
    event_type_id: int = Field(alias="EventTypeID")
    event_type_name: NameObject = Field(alias="EventTypeName")

class EventEntity(BaseSchema):
    entity_id: int = Field(alias="EntityID")
    entity_name: NameObject = Field(alias="EntityName")
    
# Requests


# Responses
class EventResponse(BaseSchema):
    event_id: int = Field(alias="EventID")
    event_name: NameObject = Field(alias="EventName")
    event_start_date: date = Field(alias="EventStartDate")
    event_end_date: Optional[date] = Field(alias="EventEndDate")
    event_location: Optional[str] = Field(alias="EventLocation")
    is_multi_team: bool = Field(alias="IsMultiTeam")
    event_type: EventType = Field(alias="EventType")
    organizing_entity: EventEntity = Field(alias="OrganizingEntity")
    participating_entities: list[EventEntity] = Field(alias="ParticipatingEntities")
    
    
class SearchEventsResponse(BaseSchema):
    events: list[EventResponse] = Field(alias="Events")
