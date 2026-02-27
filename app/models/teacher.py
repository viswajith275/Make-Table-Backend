from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
# import uuid    use as a secondary level of primary for security
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from app.db.base_class import Base

class Teacher(Base):

    __tablename__ = 'teachers' # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    max_classes_week: Mapped[Optional[int]] = mapped_column()
    max_classes_day: Mapped[Optional[int]] = mapped_column()
    max_classes_consecutive: Mapped[Optional[int]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())

    timetable_id: Mapped[int] = mapped_column(ForeignKey('timetables.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    #relationships
    user: Mapped['User'] = relationship("User", back_populates='teachers') # type: ignore
    timetable: Mapped['TimeTable'] = relationship("TimeTable", back_populates='teachers') # type: ignore
    assignments: Mapped[List['TeacherAssignment']] = relationship("TeacherAssignment", back_populates='teacher', cascade='all, delete-orphan') # type: ignore
    entries: Mapped[List['TimeTableEntry']] = relationship("TimeTableEntry", back_populates='teacher', cascade='all, delete-orphan') # type: ignore