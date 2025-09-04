from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base


class AttendanceState(Base):
    __tablename__ = "attendance_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    attendance_state_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    attendance_state_name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    attendance_state_name_ar: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationship with Attendance
    attendance_records = relationship("Attendance", back_populates="attendance_state")
