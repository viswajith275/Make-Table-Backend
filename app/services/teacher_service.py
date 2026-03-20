from typing import Dict, List

from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.exceptions import BadRequest, Conflict, NotFound
from app.models.enums import TimeTableStatus
from app.models.teacher import Teacher
from app.models.timetable import TimeTable
from app.schemas.teacher import TeacherCreate, TeacherUpdate


async def create_teacher(
    timetable_id: int, user_id: int, teacher_request: TeacherCreate, db: AsyncSession
) -> Teacher:

    stmt = await db.execute(
        select(TimeTable).where(
            TimeTable.id == timetable_id, TimeTable.user_id == user_id
        )
    )
    timetable = stmt.scalar_one_or_none()

    if timetable is None:
        raise NotFound("TimeTable not found!")

    if timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")

    stmt = await db.execute(
        select(
            exists().where(
                Teacher.name == teacher_request.name,
                Teacher.timetable_id == timetable.id,
            )
        )
    )
    existing = stmt.scalar()

    if existing:
        raise Conflict("This teacher already exists!")

    teacher_obj = Teacher(
        name=teacher_request.name,
        max_classes_day=teacher_request.max_classes_day,
        max_classes_week=teacher_request.max_classes_week,
        max_classes_consecutive=teacher_request.max_classes_consecutive,
        timetable_id=timetable.id,
        user_id=user_id,
    )

    db.add(teacher_obj)
    await db.commit()
    await db.refresh(teacher_obj)

    return teacher_obj


async def fetch_timetable_teachers(
    timetable_id: int, user_id: int, db: AsyncSession
) -> List[Teacher]:

    stmt = await db.execute(
        select(TimeTable)
        .where(TimeTable.id == timetable_id, TimeTable.user_id == user_id)
        .options(selectinload(TimeTable.teachers))
    )
    timetable = stmt.scalar_one_or_none()

    if timetable is None or not timetable.teachers:
        raise NotFound("No teachers found!")

    return timetable.teachers


async def fetch_teacher(user_id: int, teacher_id: int, db: AsyncSession) -> Teacher:

    stmt = await db.execute(
        select(Teacher).where(Teacher.id == teacher_id, Teacher.user_id == user_id)
    )
    teacher_obj = stmt.scalar_one_or_none()

    if teacher_obj is None:
        raise NotFound("Teacher not found!")

    return teacher_obj


async def update_teacher(
    timetable_id: int,
    user_id: int,
    teacher_id: int,
    teacher_patch: TeacherUpdate,
    db: AsyncSession,
) -> Teacher:

    patch_data = teacher_patch.model_dump(exclude_unset=True)

    if not patch_data:
        raise BadRequest("Nothing to update!")

    teacher_name = patch_data.get("name")
    if teacher_name is not None:
        stmt = await db.execute(
            select(
                exists().where(
                    Teacher.name == teacher_name,
                    Teacher.timetable_id == timetable_id,
                    Teacher.user_id == user_id,
                )
            )
        )
        existing = stmt.scalar()

        if existing:
            raise Conflict("This teacher already exists!")

    stmt = await db.execute(
        select(TimeTable).where(
            TimeTable.id == timetable_id, TimeTable.user_id == user_id
        )
    )
    timetable = stmt.scalar_one_or_none()

    if timetable is not None and timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")

    stmt = await db.execute(
        (
            update(Teacher)
            .where(Teacher.id == teacher_id, Teacher.user_id == user_id)
            .values(**patch_data)
            .returning(Teacher)
        )
    )
    teacher_obj = stmt.scalar_one_or_none()

    if not teacher_obj:
        raise NotFound("Teacher not found!")

    await db.commit()

    return teacher_obj


async def delete_teacher(
    teacher_id: int, user_id: int, db: AsyncSession
) -> Dict[str, str]:

    stmt = await db.execute(
        select(Teacher)
        .where(Teacher.id == teacher_id, Teacher.user_id == user_id)
        .options(joinedload(Teacher.timetable))
    )
    teacher = stmt.scalar_one_or_none()

    if teacher is None:
        raise NotFound("Teacher not found!")

    if teacher.timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")

    await db.delete(teacher)

    await db.commit()

    return {"message": f"Teacher with id {teacher_id} deleted successfully"}
