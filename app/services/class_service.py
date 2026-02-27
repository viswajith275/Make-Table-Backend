from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session
from typing import List, Dict
from app.models.class_ import Class
from app.models.timetable import TimeTable
from app.schemas.class_ import ClassCreate, ClassUpdate
from app.core.exceptions import NotFound, BadRequest, Conflict
from app.models.enums import TimeTableStatus

def create_class(timetable_id: int, user_id: int, class_request: ClassCreate, db: Session) -> Class:

    stmt = select(TimeTable).where(TimeTable.id == timetable_id, TimeTable.user_id == user_id)
    timetable = db.scalars(stmt).first()

    if timetable is None:
        raise NotFound(message="TimeTable not found!")

    # if needed add a constraint to check existing class
    stmt = select(Class).where(Class.class_name == class_request.class_name, Class.timetable_id == timetable.id)
    existing = db.scalars(stmt).first()

    if existing:
        raise Conflict("This class already exists!")

    class_obj = Class(class_name=class_request.class_name,
                      room_name=class_request.room_name,
                      isLab=class_request.isLab,
                      timetable_id=timetable.id,
                      user_id=user_id
                      )
    
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)

    return class_obj



def fetch_timetable_classes(timetable_id: int, user_id: int, db: Session) -> List[Class]:
    stmt = select(TimeTable).where(TimeTable.id == timetable_id, TimeTable.user_id == user_id)
    timetable = db.scalars(stmt).first()

    if timetable is None or not timetable.classes:
        raise NotFound("No classes found!")
    
    return timetable.classes



def update_class(timetable_id: int, class_id: int, user_id: int, class_patch: ClassUpdate, db: Session) -> Class:

    patch_data = class_patch.model_dump(exclude_unset=True)

    if not patch_data:
        raise BadRequest("Nothing to update!")
    
    class_name = patch_data.get('class_name')

    if class_name is not None:

        stmt = select(Class).where(Class.class_name == class_name, Class.timetable_id == timetable_id, Class.user_id == user_id)
        existing = db.scalars(stmt).first()

        if existing:
            raise Conflict("This class already exists!")
        
    stmt = update(Class).where(Class.id == class_id, Class.user_id == user_id).values(**patch_data).returning(Class)
    class_obj = db.execute(stmt).scalar_one_or_none()

    if not class_obj:
        raise NotFound("Class not found!")
    
    db.commit()

    return class_obj


def delete_class(class_id: int, user_id: int, db: Session) -> Dict[str, str]:

    stmt = delete(Class).where(Class.id == class_id, Class.user_id == user_id).returning(Class.id)
    deleted_id = db.execute(stmt).scalar_one_or_none()

    if deleted_id is None:
        raise NotFound("Class not found!")
    
    db.commit()

    return {
        'message': f'Class with id {deleted_id} deleted successfully'
    }