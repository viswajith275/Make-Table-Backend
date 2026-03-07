from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List

from app.models.class_ import Class
from app.models.teacher import Teacher
from app.models.timetable_entry import TimeTableEntry
from app.models.enums import TimeTableStatus
from app.core.exceptions import NotFound, BadRequest


def fetch_class_entries(class_id: int, user_id: int, db: Session) -> List[TimeTableEntry]:

    stmt = select(Class).where(Class.id == class_id, Class.user_id == user_id)
    class_ = db.scalars(stmt).one_or_none()

    if class_ is None:
        raise NotFound("Class not found!")
    
    if class_.timetable.status == TimeTableStatus.Processing:
        raise BadRequest("The timetable entries are being updated!")
    
    if not class_.entries:
        raise NotFound("No entries found!")
    
    return class_.entries



def fetch_teacher_entries(teacher_id: int, user_id: int, db: Session) -> List[TimeTableEntry]:

    stmt = select(Teacher).where(Teacher.id == teacher_id, Teacher.user_id == user_id)
    teacher = db.scalars(stmt).one_or_none()

    if teacher is None:
        raise NotFound("Class not found!")
    
    if teacher.timetable.status == TimeTableStatus.Processing:
        raise BadRequest("The timetable entries are being updated!")
    
    if not teacher.entries:
        raise NotFound("No entries found!")
    
    return teacher.entries
