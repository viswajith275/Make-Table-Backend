from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
# import uuid    use as a secondary level of primary for security
from datetime import datetime
from typing import Optional
from app.db.base_class import Base
from app.models.enums import WeekDayEnum

class TimeTableEntry(Base):

    __tablename__ = 'timetable_entries'  # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    day: Mapped[WeekDayEnum] = mapped_column()
    slot: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    timetable_id: Mapped[int] = mapped_column(ForeignKey('timetables.id'))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    lab_id: Mapped[Optional[int]] = mapped_column(ForeignKey('classes.id'))


    #relationships
    user: Mapped['User'] = relationship("User", back_populates='entries') # type: ignore
    timetable: Mapped['TimeTable'] = relationship("TimeTable", back_populates='entries') # type: ignore
    teacher: Mapped['Teacher'] = relationship("Teacher", back_populates="entries") # type: ignore
    class_: Mapped['Class'] = relationship("Class", back_populates="entries", foreign_keys=[class_id]) # type: ignore
    subject: Mapped['Subject'] = relationship("Subject", back_populates="entries")  # type: ignore
    lab: Mapped['Class'] = relationship("Class", back_populates="lab_entries", foreign_keys=[lab_id]) # type: ignore