from typing import Dict, List

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequest, Conflict, NotFound
from app.models.enums import TimeTableStatus
from app.models.timetable import TimeTable
from app.schemas.timetable import TimeTableCreate, TimeTableUpdate
from app.worker import tasks


async def create_timetable(
    user_id: int, timetable_request: TimeTableCreate, db: AsyncSession
) -> TimeTable:

    timetable_obj = TimeTable(
        name=timetable_request.name,
        slots=timetable_request.slots,
        days=timetable_request.days,
        user_id=user_id,
    )

    db.add(timetable_obj)
    await db.commit()
    await db.refresh(timetable_obj)

    return timetable_obj


async def fetch_all_timetables(user_id: int, db: AsyncSession) -> List[TimeTable]:

    stmt = await db.execute(select(TimeTable).where(TimeTable.user_id == user_id))
    timetable_objs = stmt.scalars().all()

    if not timetable_objs:
        raise NotFound("No timetables found!")

    return timetable_objs  # type: ignore


async def update_timetable(
    timetable_id: int, user_id: int, timetable_patch: TimeTableUpdate, db: AsyncSession
) -> TimeTable:

    updated_data = timetable_patch.model_dump(exclude_unset=True)

    if not updated_data:
        raise BadRequest("Nothing to update!")

    stmt = await db.execute(
        update(TimeTable)
        .where(TimeTable.id == timetable_id, TimeTable.user_id == user_id)
        .values(**updated_data)
        .returning(TimeTable)
    )
    timetable_obj = stmt.scalar_one_or_none()

    if timetable_obj is None:
        raise NotFound("TimeTable does not exists!")

    await db.commit()

    return timetable_obj


async def delete_timetable(
    timetable_id: int, user_id: int, db: AsyncSession
) -> Dict[str, str]:

    stmt = await db.execute(
        delete(TimeTable)
        .where(TimeTable.id == timetable_id, TimeTable.user_id == user_id)
        .returning(TimeTable.id)
    )
    deleted_id = stmt.scalar_one_or_none()

    if deleted_id is None:
        raise NotFound("TimeTable not found!")

    await db.commit()

    return {"message": f"timetable with id {deleted_id} deleted successfully!"}


async def generate_timetable_task(
    timetable_id: int, user_id: int, db: AsyncSession, force_generation: bool = False
) -> TimeTable:

    stmt = await db.execute(
        select(TimeTable).where(
            TimeTable.id == timetable_id, TimeTable.user_id == user_id
        )
    )
    timetable = stmt.scalar_one_or_none()

    if timetable is None:
        raise NotFound("TimeTable not found!")

    if timetable.status == TimeTableStatus.Processing:
        raise Conflict("The TimeTable is already being processed!")

    tasks.generate_timetable_task.delay(
        timetable_id=timetable_id, user_id=user_id, force_generation=force_generation
    )

    return timetable


async def current_timetable_status(
    timetable_id: int, user_id: int, db: AsyncSession
) -> TimeTable:

    stmt = await db.execute(
        select(TimeTable).where(
            TimeTable.id == timetable_id, TimeTable.user_id == user_id
        )
    )
    timetable = stmt.scalar_one_or_none()

    if timetable is None:
        raise NotFound("TimeTable not found!")

    return timetable
