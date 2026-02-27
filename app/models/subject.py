from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
# import uuid    use as a secondary level of primary for security
from datetime import datetime
from typing import Optional, List
from app.db.base_class import Base
from app.models.enums import Hardness
from app.models.assocoations import LabAssignment

class Subject(Base):

    __tablename__ = 'subjects' # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    
    min_classes_day: Mapped[Optional[int]] = mapped_column()
    max_classes_day: Mapped[Optional[int]] = mapped_column()
    min_classes_week: Mapped[Optional[int]] = mapped_column()
    max_classes_week: Mapped[Optional[int]] = mapped_column()
    min_classes_consecutive: Mapped[Optional[int]] = mapped_column()
    max_classes_consecutive: Mapped[Optional[int]] = mapped_column()
    isLab: Mapped[bool] = mapped_column(default=False)
    hardness: Mapped[Hardness] = mapped_column(default=Hardness.low)

    timetable_id: Mapped[int] = mapped_column(ForeignKey('timetables.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    #relationships
    user: Mapped['User'] = relationship("User", back_populates='subjects') # type: ignore
    timetable: Mapped['TimeTable'] = relationship("TimeTable", back_populates='subjects') # type: ignore
    lab_classes: Mapped[List['Class']] = relationship("Class", secondary=LabAssignment, passive_deletes=True, back_populates='assigned_labs') # type: ignore
    assignments: Mapped[List['TeacherAssignment']] = relationship("TeacherAssignment", back_populates='subject', cascade='all, delete-orphan') # type: ignore
    entries: Mapped[List['TimeTableEntry']] = relationship("TimeTableEntry", back_populates='subject', cascade='all, delete-orphan') # type: ignore