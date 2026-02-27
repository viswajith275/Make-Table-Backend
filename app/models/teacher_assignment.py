from sqlalchemy import ForeignKey, Enum, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
# import uuid    use as a secondary level of primary for security
from datetime import datetime
from typing import Optional, List
from app.db.base_class import Base
from app.models.enums import WeekDayEnum, TeacherRole


class TeacherAssignment(Base):

    __tablename__ = 'teacher_assignments' # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())

    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))

    role: Mapped[TeacherRole] = mapped_column(Enum(TeacherRole), default=TeacherRole.subject_teacher)
    morning_class_days: Mapped[Optional[List[WeekDayEnum]]] = mapped_column(ARRAY(Enum(WeekDayEnum)))

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    timetable_id: Mapped[int] = mapped_column(ForeignKey('timetables.id'))

    #relationships
    user: Mapped['User'] = relationship("User", back_populates="assignments") # type: ignore
    timetable: Mapped['TimeTable'] = relationship("TimeTable", back_populates="assignments") # type: ignore
    teacher: Mapped['Teacher'] = relationship("Teacher", back_populates="assignments") # type: ignore
    class_: Mapped['Class'] = relationship("Class", back_populates="assignments") # type: ignore
    subject: Mapped['Subject'] = relationship("Subject", back_populates="assignments")  # type: ignore