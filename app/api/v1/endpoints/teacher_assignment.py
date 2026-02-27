from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.services import teacher_assignment_service
from app.schemas import teacher_assignment
from app.models.user import User


router = APIRouter()


@router.get('/teachers/{teacher_id}/assignments', response_model=List[teacher_assignment.TeacherAssignmentResponse])
def fetch_teacher_assignemnts(request: Request,
                              teacher_id: int,
                              current_user: User = Depends(deps.get_current_active_user),
                              db: Session = Depends(deps.get_db)
                              ):
    
    return teacher_assignment_service.fetch_teacher_assignments(teacher_id=teacher_id,
                                                                user_id=current_user.id,
                                                                db=db
                                                                )



@router.post('/assignments', response_model=teacher_assignment.TeacherAssignmentResponse)
def create_assignment(request: Request,
                      assignment_request: teacher_assignment.TeacherAssignmentCreate,
                      current_user: User = Depends(deps.get_current_active_user),
                      db: Session = Depends(deps.get_db)):
    
    return teacher_assignment_service.create_assignment(user_id=current_user.id,
                                                        assignment_request=assignment_request,
                                                        db=db)



@router.patch('/assignments/{id}', response_model=teacher_assignment.TeacherAssignmentResponse)
def update_assignment(request: Request,
                      id: int,
                      assignment_patch: teacher_assignment.TeacherAssignmentUpdate,
                      current_user: User = Depends(deps.get_current_active_user),
                      db: Session = Depends(deps.get_db)):
    
    return teacher_assignment_service.update_assignment(assignment_id=id,
                                                        user_id=current_user.id,
                                                        assignment_patch=assignment_patch,
                                                        db=db)

@router.delete('/assignments/{id}')
def delete_assignment(request: Request,
                      id: int,
                      current_user: User = Depends(deps.get_current_active_user),
                      db: Session = Depends(deps.get_db)):
    
    return teacher_assignment_service.delete_assignment(assignment_id=id,
                                                        user_id=current_user.id,
                                                        db=db)