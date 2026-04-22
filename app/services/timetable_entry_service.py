from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.exceptions import BadRequest, NotFound
from app.models.class_ import Class
from app.models.enums import TimeTableStatus, TimeTableViewStatus
from app.models.teacher import Teacher
from app.models.timetable_entry import TimeTableEntry


async def fetch_class_entries(class_id: int, user_id: int, db: AsyncSession) -> Class:

    stmt = await db.execute(
        select(Class)
        .where(Class.id == class_id)
        .options(
            joinedload(Class.timetable),
            selectinload(Class.entries).options(
                joinedload(TimeTableEntry.class_),
                joinedload(TimeTableEntry.teacher),
                joinedload(TimeTableEntry.subject),
            ),
        )
    )
    class_ = stmt.scalar_one_or_none()

    if class_ is None:
        raise NotFound("Class not found!")

    if (
        class_.timetable.view_status == TimeTableViewStatus.Private
        and class_.user_id != user_id
    ):
        raise NotFound("Class not found")

    if class_.timetable.status == TimeTableStatus.Processing:
        raise BadRequest("The timetable entries are being updated!")

    return class_


async def fetch_teacher_entries(
    teacher_id: int, user_id: int, db: AsyncSession
) -> Teacher:

    stmt = await db.execute(
        select(Teacher)
        .where(Teacher.id == teacher_id)
        .options(
            joinedload(Teacher.timetable),
            selectinload(Teacher.entries).options(
                joinedload(TimeTableEntry.class_),
                joinedload(TimeTableEntry.teacher),
                joinedload(TimeTableEntry.subject),
            ),
        )
    )
    teacher = stmt.scalar_one_or_none()

    if teacher is None:
        raise NotFound("Teacher not found!")

    if (
        teacher.timetable.view_status == TimeTableViewStatus.Private
        and teacher.user_id != user_id
    ):
        raise NotFound("Teacher not found")

    if teacher.timetable.status == TimeTableStatus.Processing:
        raise BadRequest("The timetable entries are being updated!")

    return teacher
