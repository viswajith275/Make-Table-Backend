from typing import Dict, List

from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.exceptions import BadRequest, Conflict, NotFound
from app.models.class_ import Class
from app.models.enums import TimeTableStatus
from app.models.subject import Subject
from app.models.timetable import TimeTable
from app.schemas.subject import SubjectCreate, SubjectUpdate


async def create_subject(
    timetable_id: int, user_id: int, subject_request: SubjectCreate, db: AsyncSession
) -> Subject:

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

    stmt = await db.execute(
        select(
            exists().where(
                Subject.name == subject_request.name,
                Subject.timetable_id == timetable.id,
            )
        )
    )
    existing = stmt.scalar()

    if existing:
        raise Conflict("This subject already exists!")
    try:
        subject_obj = Subject(
            name=subject_request.name,
            min_classes_day=subject_request.min_classes_day,
            max_classes_day=subject_request.max_classes_day,
            min_classes_week=subject_request.min_classes_week,
            max_classes_week=subject_request.max_classes_week,
            min_classes_consecutive=subject_request.min_classes_consecutive,
            max_classes_consecutive=subject_request.max_classes_consecutive,
            isLab=subject_request.isLab,
            hardness=subject_request.hardness,
            timetable_id=timetable.id,
            user_id=user_id,
        )

        db.add(subject_obj)
        await db.flush()
        await db.refresh(subject_obj)

        stmt = await db.execute(
            select(Subject)
            .where(Subject.id == subject_obj.id)
            .options(selectinload(Subject.lab_classes))
        )
        subject_obj = stmt.scalar_one_or_none()

        if subject_obj is None:
            raise NotFound("Error!")

        if subject_request.isLab and subject_request.lab_classes is not None:
            for id in subject_request.lab_classes:
                stmt = await db.execute(
                    select(Class).where(
                        Class.id == id,
                        Class.timetable_id == timetable.id,
                        Class.isLab,
                    )
                )
                lab_class = stmt.scalar_one_or_none()

                if lab_class is None:
                    raise NotFound("Lab class not found!")

                subject_obj.lab_classes.append(lab_class)

        await db.commit()

    except Exception as e:
        await db.rollback()
        raise e

    return subject_obj


async def fetch_timetable_subjects(
    timetable_id: int, user_id: int, db: AsyncSession
) -> List[Subject]:

    stmt = await db.execute(
        select(TimeTable)
        .where(TimeTable.id == timetable_id, TimeTable.user_id == user_id)
        .options(selectinload(TimeTable.subjects))
    )
    timetable = stmt.scalar_one_or_none()

    if timetable is None or not timetable.subjects:
        raise NotFound("No subjects found!")

    return timetable.subjects


async def fetch_subject(user_id: int, subject_id: int, db: AsyncSession) -> Subject:

    stmt = await db.execute(
        select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
    )
    subject_obj = stmt.scalar_one_or_none()

    if subject_obj is None:
        raise NotFound("Subject not found!")

    return subject_obj


async def update_subject(
    timetable_id: int,
    user_id: int,
    subject_id: int,
    subject_patch: SubjectUpdate,
    db: AsyncSession,
) -> Subject:

    patch_data = subject_patch.model_dump(exclude_unset=True)

    if not patch_data:
        raise BadRequest("Nothing to update!")

    subject_name = patch_data.get("name")
    if subject_name is not None:
        stmt = await db.execute(
            select(
                exists().where(
                    Subject.name == subject_name,
                    Subject.timetable_id == timetable_id,
                    Subject.user_id == user_id,
                )
            )
        )
        existing = stmt.scalar()

        if existing:
            raise Conflict("This Subject already exists!")

    stmt = await db.execute(
        select(TimeTable).where(
            TimeTable.id == timetable_id, TimeTable.user_id == user_id
        )
    )
    timetable = stmt.scalar_one_or_none()

    if timetable is not None and timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")

    lab_classes = patch_data.pop("lab_classes", None)

    if patch_data:
        stmt = await db.execute(
            (
                update(Subject)
                .where(Subject.id == subject_id, Subject.user_id == user_id)
                .values(**patch_data)
                .returning(Subject)
            )
        )
        subject_obj = stmt.scalar_one_or_none()

    else:
        stmt = await db.execute(
            select(Subject)
            .where(Subject.id == subject_id, Subject.user_id == user_id)
            .options(selectinload(Subject.lab_classes))
        )
        subject_obj = stmt.scalar_one_or_none()

    if subject_obj is None:
        raise NotFound("Subject not found!")

    try:
        if lab_classes is not None and subject_obj.isLab:
            for id in lab_classes:
                stmt = await db.execute(
                    select(Class).where(
                        Class.id == id,
                        Class.timetable_id == timetable_id,
                        Class.isLab,
                    )
                )
                lab_class = stmt.scalar_one_or_none()

                if lab_class is None:
                    raise NotFound("Lab class not found!")

                if lab_class not in subject_obj.lab_classes:
                    subject_obj.lab_classes.append(lab_class)

        await db.commit()

    except Exception as e:
        await db.rollback()

        raise e

    return subject_obj


async def delete_subject(
    user_id: int, subject_id: int, db: AsyncSession
) -> Dict[str, str]:

    stmt = await db.execute(
        select(Subject)
        .where(Subject.id == subject_id, Subject.user_id == user_id)
        .options(joinedload(Subject.timetable))
    )
    subject = stmt.scalar_one_or_none()

    if subject is None:
        raise NotFound("Subject not found!")

    if subject.timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")

    await db.delete(subject)

    await db.commit()

    return {"message": f"Subject with id {subject_id} deleted successfully!"}
