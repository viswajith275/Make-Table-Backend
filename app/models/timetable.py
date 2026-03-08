# import uuid    use as a secondary level of primary for security
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import ARRAY, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import TimeTableStatus, WeekDayEnum


class TimeTable(Base):
    __tablename__ = "timetables"  # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    slots: Mapped[int] = (
        mapped_column()
    )  # Add type of timetable for diffrent timetables
    days: Mapped[List[WeekDayEnum]] = mapped_column(ARRAY(Enum(WeekDayEnum)))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())

    status: Mapped[TimeTableStatus] = mapped_column(
        Enum(TimeTableStatus), default=TimeTableStatus.Active
    )
    violations: Mapped[Optional[List[Dict]]] = mapped_column(JSONB)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="timetables")  # type: ignore
    teachers: Mapped[List["Teacher"]] = relationship(
        "Teacher", back_populates="timetable", cascade="all, delete-orphan"
    )  # type: ignore
    classes: Mapped[List["Class"]] = relationship(
        "Class", back_populates="timetable", cascade="all, delete-orphan"
    )  # type: ignore
    subjects: Mapped[List["Subject"]] = relationship(
        "Subject", back_populates="timetable", cascade="all, delete-orphan"
    )  # type: ignore
    assignments: Mapped[List["TeacherAssignment"]] = relationship(
        "TeacherAssignment", back_populates="timetable", cascade="all, delete-orphan"
    )  # type: ignore
    entries: Mapped[List["TimeTableEntry"]] = relationship(
        "TimeTableEntry", back_populates="timetable", cascade="all, delete-orphan"
    )  # type: ignore
