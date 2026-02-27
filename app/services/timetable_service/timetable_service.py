from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session
from typing import List, Dict
from app.models.timetable import TimeTable
from app.schemas.timetable import TimeTableCreate, TimeTableUpdate
from app.core.exceptions import NotFound, BadRequest

def create_timetable(user_id: int, timetable_request: TimeTableCreate, db: Session) -> TimeTable:

    timetable_obj = TimeTable(
        name=timetable_request.name,
        slots=timetable_request.slots,
        days=timetable_request.days,
        user_id=user_id
    )

    db.add(timetable_obj)
    db.commit()
    db.refresh(timetable_obj)

    return timetable_obj


def fetch_all_timetables(user_id: int, db: Session) -> List[TimeTable]:

    stmt = select(TimeTable).where(TimeTable.user_id == user_id)
    timetable_objs = db.scalars(stmt).all()

    if not timetable_objs:
        raise NotFound("No timetables found!")

    return timetable_objs # type: ignore


def update_timetable(timetable_id: int, user_id: int, timetable_patch: TimeTableUpdate, db: Session) -> TimeTable:

    updated_data = timetable_patch.model_dump(exclude_unset=True)

    if not updated_data:
        raise BadRequest("Nothing to update!")

    stmt = update(TimeTable).where(TimeTable.id == timetable_id, TimeTable.user_id == user_id).values(**updated_data).returning(TimeTable)
    timetable_obj = db.execute(stmt).scalar_one_or_none()

    if timetable_obj is None:
        raise NotFound("TimeTable does not exists!")
    
    db.commit()

    return timetable_obj


def delete_timetable(timetable_id: int, user_id: int, db: Session) -> Dict[str, str]:

    stmt = delete(TimeTable).where(TimeTable.id == timetable_id, TimeTable.user_id == user_id).returning(TimeTable.id)
    deleted_id = db.execute(stmt).scalar_one_or_none()

    if deleted_id is None:
        raise NotFound("TimeTable not found!")
    
    db.commit()
    
    return {
        'message': f'timetable with id {deleted_id} deleted successfully!'
    }