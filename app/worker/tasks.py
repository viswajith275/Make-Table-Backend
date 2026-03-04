from sqlalchemy import select
from typing import List


from app.core.celery import celery_app
from app.schemas.generation import TimeTableCreationData, ViolationCreate, GenerateRequest
from app.services.timetable_service.generator import TimeTableGenerator
from app.models.enums import TimeTableStatus
from app.db.session import SessionLocal
from app.models.timetable_entry import TimeTableEntry
from app.schemas.timetable_entry import TimeTableEntryCreate
from app.models.timetable import TimeTable


@celery_app.task(bind=True)
def generate_timetable_task(self, timetable_id: int, user_id: int, force_generation: bool):

    # Add force generation as optional for now just allow it

    with SessionLocal() as db:
        
        try:

            stmt = select(TimeTable).where(TimeTable.id == timetable_id, TimeTable.user_id == user_id)
            timetable = db.scalars(stmt).first()

            if timetable is None:
                return
            
            timetable_data = TimeTableCreationData.model_validate(timetable)

            builder = TimeTableGenerator(timetable_data=timetable_data)

            timetable_entries, violations = (
                builder
                .create_all_shifts()
                .add_class_constraints()
                .add_teacher_constaints()
                .add_subject_constraints()
                .add_teacher_assignment_constraints()
                .maximize_allocation_of_assignment()
                .minimize_and_compile()
                .solve_and_generate()
            )

            all_entries: List[TimeTableEntry] = []

            for entry in timetable_entries:

                new_entry = TimeTableEntry(
                    day=entry.day,
                    slot=entry.slot,
                    user_id=user_id,
                    timetable_id=timetable.id,
                    teacher_id=entry.teacher_id,
                    class_id=entry.class_id,
                    subject_id=entry.subject_id,
                    lab_id=entry.lab_id
                )

                all_entries.append(new_entry)

            db.add_all(all_entries)

            timetable.violations = [violation.model_dump() for violation in violations]

            timetable.status = TimeTableStatus.active

            db.commit()

        except Exception as e:

            db.rollback()

            if timetable is not None:
                timetable.status = TimeTableStatus.active

            db.commit()

            raise e