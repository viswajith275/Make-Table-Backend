from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
# import uuid    use as a secondary level of primary for security
from datetime import datetime
from typing import List, TYPE_CHECKING
from app.db.base_class import Base
from app.models.assocoations import LabAssignment

class Class(Base):

    __tablename__ = 'classes' # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    class_name: Mapped[str] = mapped_column()
    room_name: Mapped[str] = mapped_column()
    isLab: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())

    timetable_id: Mapped[int] = mapped_column(ForeignKey('timetables.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    #relationships
    user: Mapped['User'] = relationship("User", back_populates='classes') # type: ignore
    timetable: Mapped['TimeTable'] = relationship("TimeTable", back_populates='classes') # type: ignore
    assigned_labs: Mapped[List['Subject']] = relationship("Subject", secondary=LabAssignment, passive_deletes=True, back_populates='lab_classes') # type: ignore
    assignments: Mapped[List['TeacherAssignment']] = relationship("TeacherAssignment", back_populates='class_', cascade='all, delete-orphan') # type: ignore
    entries: Mapped[List['TimeTableEntry']] = relationship("TimeTableEntry", back_populates='class_', cascade='all, delete-orphan', foreign_keys="TimeTableEntry.class_id") # type: ignore
    lab_entries: Mapped[List['TimeTableEntry']] = relationship("TimeTableEntry", back_populates='lab', cascade="all, delete-orphan", foreign_keys="TimeTableEntry.lab_id") # type: ignore
