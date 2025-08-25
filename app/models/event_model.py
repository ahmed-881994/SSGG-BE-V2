from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base


class Event(Base):
    """Model representing events in the system.
    
    Maps to the 'events' table in the database.
    Contains event scheduling, location, and team information.
    """
    
    __tablename__ = "events"
    
    # Primary key
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="Unique identifier for the event")
    
    # Event identification
    event_id:Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True, autoincrement=True, comment="External event identifier")

    # Event type (foreign key reference)
    event_type_id:Mapped[int] = mapped_column(Integer, ForeignKey("event_types.event_type_id"), nullable=False, comment="Type of event (meeting, training, etc.)")
    
    # Bilingual event names
    event_name_en: Mapped[str] = mapped_column(String(45), nullable=True, comment="Event name in English")
    event_name_ar: Mapped[str] = mapped_column(String(45), nullable=True, comment="Event name in Arabic")

    # Event details
    event_location: Mapped[str] = mapped_column(String(45), nullable=True, comment="Location where the event takes place")
    event_start_date: Mapped[Date] = mapped_column(Date, nullable=False, comment="Start date of the event")
    event_end_date: Mapped[Date] = mapped_column(Date, nullable=True, comment="End date of the event (optional for single-day events)")

    # Team and multi-team flags
    is_multi_team: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False, comment="Whether the event involves multiple teams")
    organizing_entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("entities.entity_id"), nullable=False, comment="Primary entity associated with the event")


    # Relationships
    event_type = relationship("EventType", back_populates="events")
    organizing_entity = relationship("Entity", foreign_keys=[organizing_entity_id], back_populates="organized_events")

    # Many-to-many relationship for all participating entities
    event_entities: Mapped[list["EventEntity"]] = relationship("EventEntity", back_populates="event", cascade="all, delete-orphan")
    participating_entities: Mapped[list["Entity"]] = relationship("Entity", secondary="event_entities", back_populates="participated_events", viewonly=True)

    # Attendance records for the event
    attendance_records = relationship("Attendance", back_populates="event")

    def __repr__(self) -> str:
        return f"<Event(id={self.id}, name={self.event_name_en})>"