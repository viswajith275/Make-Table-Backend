from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session
from typing import List, Dict
from app.models.subject import Subject
from app.models.class_ import Class
from app.models.timetable import TimeTable
from app.schemas.subject import SubjectCreate, SubjectUpdate
from app.core.exceptions import NotFound, BadRequest, Conflict

def create_subject(timetable_id: int, user_id: int, subject_request: SubjectCreate, db: Session) -> Subject:
    
    stmt = select(TimeTable).where(TimeTable.id == timetable_id, TimeTable.user_id == user_id)
    timetable = db.scalars(stmt).first()

    if timetable is None:
        raise NotFound(message="TimeTable not found!")
    
    stmt = select(Subject).where(Subject.name == subject_request.name, Subject.timetable_id == timetable.id)
    existing = db.scalars(stmt).first()

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
            user_id=user_id
        )

        db.add(subject_obj)
        db.flush()
        db.refresh(subject_obj)

        if subject_request.isLab and subject_request.lab_classes is not None:

            for id in subject_request.lab_classes:
                
                stmt = select(Class).where(Class.id == id, Class.timetable_id == timetable.id, Class.isLab == True)
                lab_class = db.scalars(stmt).first()

                if lab_class is None:
                    raise NotFound("Lab class not found!")
                
                subject_obj.lab_classes.append(lab_class)

        db.commit()

    except:

        db.rollback()
        raise NotFound("Lab class not found!")
    

    return subject_obj


def fetch_timetable_subjects(timetable_id: int, user_id: int, db: Session) -> List[Subject]:

    stmt = select(TimeTable).where(TimeTable.id == timetable_id, TimeTable.user_id == user_id)
    timetable = db.scalars(stmt).first()

    if timetable is None or not timetable.subjects:
        raise NotFound("No subjects found!")
    
    return timetable.subjects



def fetch_subject(user_id: int, subject_id: int, db: Session) -> Subject:

    stmt = select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
    subject_obj = db.scalars(stmt).first()

    if subject_obj is None:
        raise NotFound("Subject not found!")
    
    return subject_obj



def update_subject(timetable_id: int, user_id: int, subject_id: int, subject_patch: SubjectUpdate, db: Session) -> Subject:

    patch_data = subject_patch.model_dump(exclude_unset=True)

    if not patch_data:
        raise BadRequest("Nothing to update!")

    subject_name = patch_data.get('name')
    if subject_name is not None:

        stmt = select(Subject).where(Subject.name == subject_name, Subject.timetable_id == timetable_id, Subject.user_id == user_id)
        existing = db.scalars(stmt).first()

        if existing:
            raise Conflict("This Subject already exists!")
    
    lab_classes = patch_data.pop('lab_classes', None)

    if patch_data:

        stmt = update(Subject).where(Subject.id == subject_id, Subject.user_id == user_id).values(**patch_data).returning(Subject)
        subject_obj = db.execute(stmt).scalar_one_or_none()

    else:

        stmt = select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
        subject_obj = db.scalars(stmt).first()

    if not subject_obj:
        raise NotFound("Subject not found!")
    
    try:

        if lab_classes is not None and subject_obj.isLab:

            for id in lab_classes:
                
                stmt = select(Class).where(Class.id == id, Class.timetable_id == timetable_id, Class.isLab == True)
                lab_class = db.scalars(stmt).first()

                if lab_class is None:
                    raise NotFound("Lab class not found!")
                
                if lab_class not in subject_obj.lab_classes:
                    subject_obj.lab_classes.append(lab_class)

        db.commit()

    except:

        db.rollback()
        raise NotFound("Lab class not found!")


    return subject_obj



def delete_subject(user_id: int, subject_id: int, db: Session) -> Dict[str, str]:

    stms = delete(Subject).where(Subject.id == subject_id, Subject.user_id == user_id).returning(Subject.id)
    deleted_id = db.execute(stms).scalar_one_or_none()

    if deleted_id is None:
        raise NotFound("Subject not found!")
    
    db.commit()

    return {
        'message': f'Subject with id {deleted_id} deleted successfully!'
    }