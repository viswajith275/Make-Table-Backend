from sqlalchemy.orm import Mapped, mapped_column, relationship
# import uuid    use as a secondary level of primary for security
from datetime import datetime
from typing import List
from app.db.base_class import Base

class User(Base):

    __tablename__ = 'users' # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    hashed_password: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    disabled: Mapped[bool] = mapped_column(default=False)

    #Add relationships as well as they add
    tokens: Mapped[List['UserToken']] = relationship("UserToken", back_populates='user', cascade='all, delete-orphan') # type: ignore
    timetables: Mapped[List['TimeTable']] = relationship("TimeTable",back_populates='user', cascade='all, delete-orphan') # type: ignore
    classes: Mapped[List['Class']] = relationship("Class", back_populates='user', cascade='all, delete-orphan') # type: ignore
    teachers: Mapped[List['Teacher']] = relationship("Teacher", back_populates='user', cascade='all, delete-orphan') # type: ignore
    subjects: Mapped[List['Subject']] = relationship("Subject", back_populates='user', cascade='all, delete-orphan') # type: ignore
    assignments: Mapped[List['TeacherAssignment']] = relationship("TeacherAssignment", back_populates='user', cascade='all, delete-orphan') # type: ignore
    entries: Mapped[List['TimeTableEntry']] = relationship("TimeTableEntry", back_populates='user', cascade='all, delete-orphan') # type: ignore