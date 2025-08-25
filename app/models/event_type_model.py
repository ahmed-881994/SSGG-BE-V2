from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base


class EventType(Base):
    """Model representing event types in the system.
    
    Maps to the 'event_types' table in the database.
    Defines different event categories and their descriptions.
    """
    
    __tablename__ = "event_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type_id: Mapped[int] = mapped_column(Integer, unique=True, autoincrement=True)
    event_type_name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    event_type_name_ar: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    events: Mapped[list["Event"]] = relationship("Event", back_populates="event_type")
