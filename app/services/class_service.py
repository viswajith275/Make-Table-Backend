from typing import Dict, List

from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.exceptions import BadRequest, Conflict, NotFound
from app.models.class_ import Class
from app.models.enums import TimeTableStatus
from app.models.timetable import TimeTable
from app.schemas.class_ import ClassCreate, ClassUpdate


async def create_class(
    timetable_id: int, user_id: int, class_request: ClassCreate, db: AsyncSession
) -> Class:

    stmt = await db.execute(
        select(TimeTable).where(
            TimeTable.id == timetable_id, TimeTable.user_id == user_id
        )
    )
    timetable = stmt.scalar_one_or_none()

    if timetable is None:
        raise NotFound(message="TimeTable not found!")

    if timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")

    # if needed add a constraint to check existing class
    stmt = await db.execute(
        select(
            exists().where(
                Class.class_name == class_request.class_name,
                Class.timetable_id == timetable.id,
            )
        )
    )
    existing = stmt.scalar()

    if existing:
        raise Conflict("This class already exists!")

    class_obj = Class(
        class_name=class_request.class_name,
        room_name=class_request.room_name,
        isLab=class_request.isLab,
        timetable_id=timetable.id,
        user_id=user_id,
    )

    db.add(class_obj)
    await db.commit()
    await db.refresh(class_obj)

    return class_obj


async def fetch_timetable_classes(
    timetable_id: int, user_id: int, db: AsyncSession
) -> List[Class]:
    stmt = await db.execute(
        select(TimeTable)
        .where(TimeTable.id == timetable_id, TimeTable.user_id == user_id)
        .options(selectinload(TimeTable.classes))
    )
    timetable = stmt.scalar_one_or_none()

    if timetable is None:
        raise NotFound("TimeTable not found!")

    return timetable.classes


async def update_class(
    timetable_id: int,
    class_id: int,
    user_id: int,
    class_patch: ClassUpdate,
    db: AsyncSession,
) -> Class:

    patch_data = class_patch.model_dump(exclude_unset=True)

    if not patch_data:
        raise BadRequest("Nothing to update!")

    class_name = patch_data.get("class_name")

    if class_name is not None:
        stmt = await db.execute(
            select(
                exists().where(
                    Class.class_name == class_name,
                    Class.timetable_id == timetable_id,
                    Class.user_id == user_id,
                )
            )
        )
        existing = stmt.scalar()

        if existing:
            raise Conflict("This class already exists!")

    stmt = await db.execute(
        select(TimeTable).where(
            TimeTable.id == timetable_id, TimeTable.user_id == user_id
        )
    )
    timetable = stmt.scalars().first()

    if timetable is not None and timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")

    stmt = await db.execute(
        update(Class)
        .where(Class.id == class_id, Class.user_id == user_id)
        .values(**patch_data)
        .returning(Class)
    )
    class_obj = stmt.scalar_one_or_none()

    if class_obj is None:
        raise NotFound("Class not found!")

    await db.commit()

    return class_obj


async def delete_class(class_id: int, user_id: int, db: AsyncSession) -> Dict[str, str]:

    stmt = await db.execute(
        select(Class)
        .where(Class.id == class_id, Class.user_id == user_id)
        .options(joinedload(Class.timetable))
    )
    class_ = stmt.scalar_one_or_none()

    if class_ is None:
        raise NotFound("Class not found!")

    if class_.timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")

    await db.delete(class_)

    await db.commit()

    return {"message": f"Class with id {class_id} deleted successfully"}
