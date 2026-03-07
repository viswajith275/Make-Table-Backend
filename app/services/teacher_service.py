from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session
from typing import List, Dict



from app.models.teacher import Teacher
from app.models.timetable import TimeTable
from app.schemas.teacher import TeacherCreate, TeacherUpdate
from app.core.exceptions import NotFound, BadRequest, Conflict
from app.models.enums import TimeTableStatus

def create_teacher(timetable_id: int, user_id: int, teacher_request: TeacherCreate, db: Session) -> Teacher:

    stmt = select(TimeTable).where(TimeTable.id == timetable_id, TimeTable.user_id == user_id)
    timetable = db.scalars(stmt).first()

    if timetable is None:
        raise NotFound("TimeTable not found!")
    
    if timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")
    
    stmt = select(Teacher).where(Teacher.name == teacher_request.name, Teacher.timetable_id == timetable.id)
    existing = db.scalars(stmt).first()

    if existing:
        raise Conflict("This teacher already exists!")
    
    teacher_obj = Teacher(
        name=teacher_request.name,
        max_classes_day=teacher_request.max_classes_day,
        max_classes_week=teacher_request.max_classes_week,
        max_classes_consecutive=teacher_request.max_classes_consecutive,
        timetable_id=timetable.id,
        user_id=user_id
    )

    db.add(teacher_obj)
    db.commit()
    db.refresh(teacher_obj)

    return teacher_obj



def fetch_timetable_teachers(timetable_id: int, user_id: int, db: Session) -> List[Teacher]:

    stmt = select(TimeTable).where(TimeTable.id == timetable_id, TimeTable.user_id == user_id)
    timetable = db.scalars(stmt).first()

    if timetable is None or not timetable.teachers:
        raise NotFound("No teachers found!")
    
    return timetable.teachers



def fetch_teacher(user_id: int, teacher_id: int, db: Session) -> Teacher:

    stmt = select(Teacher).where(Teacher.id == teacher_id, Teacher.user_id == user_id)
    teacher_obj = db.scalars(stmt).first()

    if teacher_obj is None:
        raise NotFound("Teacher not found!")
    
    return teacher_obj



def update_teacher(timetable_id: int, user_id: int, teacher_id: int, teacher_patch: TeacherUpdate, db: Session) -> Teacher:

    patch_data = teacher_patch.model_dump(exclude_unset=True)

    if not patch_data:
        raise BadRequest("Nothing to update!")
    
    teacher_name = patch_data.get('name')
    if teacher_name is not None:

        stmt = select(Teacher).where(Teacher.name == teacher_name, Teacher.timetable_id == timetable_id, Teacher.user_id == user_id)
        existing = db.scalars(stmt).first()

        if existing:
            raise Conflict("This teacher already exists!")
    

    stmt = select(TimeTable).where(TimeTable.id == timetable_id, TimeTable.user_id == user_id)
    timetable = db.scalars(stmt).first()
    
    if timetable is not None and timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")


    stmt = update(Teacher).where(Teacher.id == teacher_id, Teacher.user_id == user_id).values(**patch_data).returning(Teacher)
    teacher_obj = db.execute(stmt).scalar_one_or_none()

    if not teacher_obj:
        raise NotFound("Teacher not found!")
    
    db.commit()

    return teacher_obj



def delete_teacher(teacher_id: int, user_id: int, db: Session) -> Dict[str, str]:

    stmt = select(Teacher).where(Teacher.id == teacher_id, Teacher.user_id == user_id)
    teacher = db.scalars(stmt).one_or_none()

    if teacher is None:
        raise NotFound("Teacher not found!")
    
    if teacher.timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")
    
    db.delete(teacher)
    
    db.commit()

    return {
        'message': f'Teacher with id {teacher_id} deleted successfully'
    }