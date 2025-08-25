from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base


class EventEntity(Base):
    """Association table for many-to-many relationship between events and entities.
    
    Allows multiple entities to participate in the same event.
    """
    
    __tablename__ = "event_entities"
    
    # Composite primary key
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"), primary_key=True, comment="Reference to the event")
    entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("entities.entity_id"), primary_key=True, comment="Reference to the participating entity")
    
    # Optional: Add role or status for the entity in this specific event
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, comment="Whether this is the primary entity")
    
    # Relationships
    event = relationship("Event", back_populates="event_entities")
    entity = relationship("Entity", back_populates="event_entities")