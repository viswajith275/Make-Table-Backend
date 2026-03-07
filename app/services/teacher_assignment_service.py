from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session
from typing import List, Dict
from app.models.teacher_assignment import TeacherAssignment
from app.models.teacher import Teacher
from app.models.class_ import Class
from app.models.subject import Subject
from app.models.enums import TimeTableStatus
from app.schemas.teacher_assignment import TeacherAssignmentCreate, TeacherAssignmentUpdate
from app.core.exceptions import NotFound, BadRequest, Conflict
from app.models.enums import TeacherRole


def create_assignment(user_id: int, assignment_request: TeacherAssignmentCreate, db: Session) -> TeacherAssignment:

    stmt = select(TeacherAssignment).where(TeacherAssignment.class_id == assignment_request.class_id,
                                           TeacherAssignment.teacher_id == assignment_request.teacher_id,
                                           TeacherAssignment.subject_id == assignment_request.subject_id
                                           )
    existing = db.scalars(stmt).first()

    if existing:
        raise Conflict("Assignment already exists!")
    

    stmt = select(Teacher).where(Teacher.id == assignment_request.teacher_id,
                                 Teacher.user_id == user_id)
    teacher = db.scalars(stmt).first()

    if teacher is None:
        raise NotFound("Tacher not found!")
    
    if teacher.timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")

    stmt = select(Class).where(Class.id == assignment_request.class_id,
                               Class.user_id == user_id,
                               Class.timetable_id == teacher.timetable_id,
                               Class.isLab == False)
    class_ = db.scalars(stmt).first()

    if class_ is None:
        raise NotFound("Class not found!")

    stmt = select(Subject).where(Subject.id == assignment_request.subject_id,
                                 Subject.user_id == user_id,
                                 Subject.timetable_id == teacher.timetable_id)
    subject = db.scalars(stmt).first()

    if subject is None:
        raise NotFound("Subject not found!")
    
    if assignment_request.role == TeacherRole.Class_Teacher:

        stmt = select(TeacherAssignment).where(TeacherAssignment.teacher_id == teacher.id,
                                               TeacherAssignment.role == TeacherRole.Class_Teacher)
        already_class_teacher = db.scalars(stmt).first()

        if already_class_teacher:
            raise Conflict("Teacher cannot be class teacher of morethan one class!")
    
    assignment_obj = TeacherAssignment(
        teacher_id=teacher.id,
        class_id=class_.id,
        subject_id=subject.id,
        role=assignment_request.role,
        morning_class_days=assignment_request.morning_class_days,
        user_id=user_id,
        timetable_id=teacher.timetable_id
    )

    db.add(assignment_obj)
    db.commit()
    db.refresh(assignment_obj)

    return assignment_obj



def fetch_teacher_assignments(teacher_id: int, user_id: int, db: Session) -> List[TeacherAssignment]:

    stmt = select(Teacher).where(Teacher.id == teacher_id, Teacher.user_id == user_id)
    teacher = db.scalars(stmt).first()

    if teacher is None or not teacher.assignments:
        raise NotFound("No assignments found!")

    return teacher.assignments



def update_assignment(assignment_id: int, user_id: int, assignment_patch: TeacherAssignmentUpdate, db: Session) -> TeacherAssignment:

    patch_data = assignment_patch.model_dump(exclude_unset=True)

    if not patch_data:
        raise BadRequest("Nothing to update!")
    
    role = patch_data.get('role')
        
    stmt = update(TeacherAssignment).where(TeacherAssignment.id == assignment_id, TeacherAssignment.user_id == user_id).values(**patch_data).returning(TeacherAssignment)
    assignment_obj = db.execute(stmt).scalar_one_or_none()

    if assignment_obj is None:
        raise NotFound("Assignment not found!")
    
    
    if assignment_obj.timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")
    
    
    if role == TeacherRole.Class_Teacher:

        stmt = select(TeacherAssignment).where(TeacherAssignment.teacher_id == assignment_obj.teacher_id,
                                               TeacherAssignment.role == TeacherRole.Class_Teacher)
        already_class_teacher = db.scalars(stmt).first()

        if already_class_teacher:
            raise Conflict("Teacher cannot be class teacher of morethan one class!")
    
    db.commit()

    return assignment_obj



def delete_assignment(assignment_id: int, user_id: int, db: Session) -> Dict[str, str]:

    stmt = select(TeacherAssignment).where(TeacherAssignment.id == assignment_id, TeacherAssignment.user_id == user_id)
    assignment = db.scalars(stmt).one_or_none()

    if assignment is None:
        raise NotFound("Subject not found!")
    
    if assignment.timetable.status == TimeTableStatus.Processing:
        raise Conflict("The timetable is being processed! wait till completion")
    
    db.delete(assignment)
    
    db.commit()
    
    return {
        'message': f'Assignment with id {assignment_id} deleted successfully!'
    }