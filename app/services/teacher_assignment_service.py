from typing import Dict, List

from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import selectinload

from app.core.exceptions import BadRequest, Conflict, NotFound
from app.models.class_ import Class
from app.models.enums import TeacherRole, TimeTableStatus
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.schemas.teacher_assignment import (
    TeacherAssignmentCreate,
    TeacherAssignmentUpdate,
)


async def create_assignment(
    user_id: int, assignment_request: TeacherAssignmentCreate, db: AsyncSession
) -> TeacherAssignment:

    stmt = await db.execute(
        select(
            exists().where(
                TeacherAssignment.class_id == assignment_request.class_id,
                TeacherAssignment.teacher_id == assignment_request.teacher_id,
                TeacherAssignment.subject_id == assignment_request.subject_id,
            )
        )
    )
    existing = stmt.scalar()

    if existing:
        raise Conflict("Assignment already exists!")

    stmt = await db.execute(
        select(Teacher)
        .where(Teacher.id == assignment_request.teacher_id, Teacher.user_id == user_id)
        .options(joinedload(Teacher.timetable))
    )
    teacher = stmt.scalar_one_or_none()

    if teacher is None:
        raise NotFound("Tacher not found!")

    if teacher.timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")

    stmt = await db.execute(
        select(Class).where(
            Class.id == assignment_request.class_id,
            Class.user_id == user_id,
            Class.timetable_id == teacher.timetable_id,
            Class.isLab == False,
        )
    )
    class_ = stmt.scalar_one_or_none()

    if class_ is None:
        raise NotFound("Class not found!")

    stmt = await db.execute(
        select(Subject).where(
            Subject.id == assignment_request.subject_id,
            Subject.user_id == user_id,
            Subject.timetable_id == teacher.timetable_id,
        )
    )
    subject = stmt.scalar_one_or_none()

    if subject is None:
        raise NotFound("Subject not found!")

    if assignment_request.role == TeacherRole.Class_Teacher:
        stmt = await db.execute(
            select(
                exists().where(
                    TeacherAssignment.teacher_id == teacher.id,
                    TeacherAssignment.role == TeacherRole.Class_Teacher,
                )
            )
        )
        already_class_teacher = stmt.scalar()

        if already_class_teacher:
            raise Conflict("Teacher cannot be class teacher of morethan one class!")

    assignment_obj = TeacherAssignment(
        teacher_id=teacher.id,
        class_id=class_.id,
        subject_id=subject.id,
        role=assignment_request.role,
        morning_class_days=assignment_request.morning_class_days,
        user_id=user_id,
        timetable_id=teacher.timetable_id,
    )

    db.add(assignment_obj)
    await db.commit()
    await db.refresh(assignment_obj)

    stmt = await db.execute(
        select(TeacherAssignment)
        .where(TeacherAssignment.id == assignment_obj.id)
        .options(
            joinedload(TeacherAssignment.subject),
            joinedload(TeacherAssignment.class_),
            joinedload(TeacherAssignment.teacher),
        )
    )

    return assignment_obj


async def fetch_teacher_assignments(
    teacher_id: int, user_id: int, db: AsyncSession
) -> List[TeacherAssignment]:

    stmt = await db.execute(
        select(Teacher)
        .where(Teacher.id == teacher_id, Teacher.user_id == user_id)
        .options(
            selectinload(Teacher.assignments).options(
                joinedload(TeacherAssignment.class_),
                joinedload(TeacherAssignment.subject),
            )
        )
    )
    teacher = stmt.scalar_one_or_none()

    if teacher is None:
        raise NotFound("TimeTable not found!")

    return teacher.assignments


async def update_assignment(
    assignment_id: int,
    user_id: int,
    assignment_patch: TeacherAssignmentUpdate,
    db: AsyncSession,
) -> TeacherAssignment:

    patch_data = assignment_patch.model_dump(exclude_unset=True)

    if not patch_data:
        raise BadRequest("Nothing to update!")

    role = patch_data.get("role")

    stmt = await db.execute(
        update(TeacherAssignment)
        .where(
            TeacherAssignment.id == assignment_id, TeacherAssignment.user_id == user_id
        )
        .options(
            joinedload(TeacherAssignment.class_), joinedload(TeacherAssignment.subject)
        )
        .values(**patch_data)
        .returning(TeacherAssignment)
    )
    assignment_obj = stmt.scalar_one_or_none()

    if assignment_obj is None:
        raise NotFound("Assignment not found!")

    if assignment_obj.timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")

    if role == TeacherRole.Class_Teacher:
        stmt = await db.execute(
            select(
                exists().where(
                    TeacherAssignment.teacher_id == assignment_obj.teacher_id,
                    TeacherAssignment.role == TeacherRole.Class_Teacher,
                )
            )
        )
        already_class_teacher = stmt.scalar()

        if already_class_teacher:
            raise Conflict("Teacher cannot be class teacher of morethan one class!")

    await db.commit()

    return assignment_obj


async def delete_assignment(
    assignment_id: int, user_id: int, db: AsyncSession
) -> Dict[str, str]:

    stmt = await db.execute(
        select(TeacherAssignment)
        .where(
            TeacherAssignment.id == assignment_id, TeacherAssignment.user_id == user_id
        )
        .options(joinedload(TeacherAssignment.timetable))
    )
    assignment = stmt.scalar_one_or_none()

    if assignment is None:
        raise NotFound("Subject not found!")

    if assignment.timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")

    await db.delete(assignment)

    await db.commit()

    return {"message": f"Assignment with id {assignment_id} deleted successfully!"}
