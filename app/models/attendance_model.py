from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base


class Attendance(Base):
    __tablename__ = "attendance"

    attendance_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    member_id: Mapped[str] = mapped_column(String(20), ForeignKey("members.member_id"), nullable=False)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.event_id"), nullable=False)
    attendance_state_id: Mapped[int] = mapped_column(Integer, ForeignKey("attendance_states.attendance_state_id"), nullable=False)

    # Relationships
    # Relationship with Member
    member = relationship("Member", back_populates="attendance_records")
    # Relationship with Event
    event = relationship("Event", back_populates="attendance_records")
    # Relationship with AttendanceState
    attendance_state = relationship("AttendanceState", back_populates="attendance_records")