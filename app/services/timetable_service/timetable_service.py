from typing import Dict, List

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequest, Conflict, NotFound
from app.models.enums import TimeTableStatus
from app.models.timetable import TimeTable
from app.schemas.timetable import TimeTableCreate, TimeTableUpdate
from app.worker import tasks


def create_timetable(
    user_id: int, timetable_request: TimeTableCreate, db: Session
) -> TimeTable:

    timetable_obj = TimeTable(
        name=timetable_request.name,
        slots=timetable_request.slots,
        days=timetable_request.days,
        user_id=user_id,
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

    return timetable_objs  # type: ignore


def update_timetable(
    timetable_id: int, user_id: int, timetable_patch: TimeTableUpdate, db: Session
) -> TimeTable:

    updated_data = timetable_patch.model_dump(exclude_unset=True)

    if not updated_data:
        raise BadRequest("Nothing to update!")

    stmt = (
        update(TimeTable)
        .where(TimeTable.id == timetable_id, TimeTable.user_id == user_id)
        .values(**updated_data)
        .returning(TimeTable)
    )
    timetable_obj = db.execute(stmt).scalar_one_or_none()

    if timetable_obj is None:
        raise NotFound("TimeTable does not exists!")

    db.commit()

    return timetable_obj


def delete_timetable(timetable_id: int, user_id: int, db: Session) -> Dict[str, str]:

    stmt = (
        delete(TimeTable)
        .where(TimeTable.id == timetable_id, TimeTable.user_id == user_id)
        .returning(TimeTable.id)
    )
    deleted_id = db.execute(stmt).scalar_one_or_none()

    if deleted_id is None:
        raise NotFound("TimeTable not found!")

    db.commit()

    return {"message": f"timetable with id {deleted_id} deleted successfully!"}


def generate_timetable_task(
    timetable_id: int, user_id: int, db: Session, force_generation: bool = False
) -> TimeTable:

    stmt = select(TimeTable).where(
        TimeTable.id == timetable_id, TimeTable.user_id == user_id
    )
    timetable = db.scalars(stmt).first()

    if timetable is None:
        raise NotFound("TimeTable not found!")

    if timetable.status == TimeTableStatus.Processing:
        raise Conflict("The TimeTable is already being processed!")

    timetable.status = TimeTableStatus.Processing

    db.commit()

    tasks.generate_timetable_task.delay(
        timetable_id=timetable_id, user_id=user_id, force_generation=force_generation
    )

    return timetable


def current_timetable_status(timetable_id: int, user_id: int, db: Session) -> TimeTable:

    stmt = select(TimeTable).where(
        TimeTable.id == timetable_id, TimeTable.user_id == user_id
    )
    timetable = db.scalars(stmt).first()

    if timetable is None:
        raise NotFound("TimeTable not found!")

    return timetable
