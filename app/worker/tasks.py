from celery import Task
from sqlalchemy import select

from app.core.celery import celery_app
from app.db.session import SyncSessionLocal
from app.models.enums import TimeTableStatus
from app.models.timetable import TimeTable
from app.models.timetable_entry import TimeTableEntry
from app.schemas.generation import TimeTableCreationData
from app.services.timetable_service.generator import TimeTableGenerator


@celery_app.task(
    bind=True,
    acks_late=True,
    soft_time_limit=120,
    time_limit=150,
)
def generate_timetable_task(
    self: Task, timetable_id: int, user_id: int, force_generation: bool
) -> None:
    # Add force generation later ## update added  new todo improve

    # Add force generation as optional for now just allow it

    with SyncSessionLocal() as db:
        try:
            stmt = select(TimeTable).where(
                TimeTable.id == timetable_id, TimeTable.user_id == user_id
            )
            timetable = db.scalars(stmt).first()

            if timetable is None:
                return

            timetable.status = TimeTableStatus.Processing
            db.commit()

            timetable_data = TimeTableCreationData.model_validate(timetable)

            builder = TimeTableGenerator(timetable_data=timetable_data)

            timetable_entries, violations = (
                builder.create_all_shifts()
                .add_class_constraints()
                .add_teacher_constaints()
                .add_subject_constraints()
                .add_teacher_assignment_constraints()
                .maximize_allocation_of_assignment()
                .minimize_and_compile()
                .solve_and_generate()
            )

            violations_data = [violation.model_dump() for violation in violations]

            if violations_data and not force_generation:
                timetable.violations = violations_data
                timetable.status = TimeTableStatus.Failed

                db.commit()

                return

            if not timetable_entries:
                timetable.status = TimeTableStatus.Failed
                db.commit()
                return

            for prev_entry in timetable.entries:
                db.delete(prev_entry)

            db.add_all(
                TimeTableEntry(
                    day=entry.day,
                    slot=entry.slot,
                    user_id=user_id,
                    timetable_id=timetable.id,
                    teacher_id=entry.teacher_id,
                    class_id=entry.class_id,
                    subject_id=entry.subject_id,
                    lab_id=entry.lab_id,
                    role=entry.role,
                )
                for entry in timetable_entries
            )

            timetable.violations = violations_data

            timetable.status = TimeTableStatus.Active

            db.commit()

        except Exception as e:  # When doing logging log this error
            db.rollback()

            stmt = select(TimeTable).where(
                TimeTable.id == timetable_id, TimeTable.user_id == user_id
            )
            timetable = db.scalars(stmt).first()

            if timetable is not None:
                timetable.status = TimeTableStatus.Failed

            db.commit()
