from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.services import subject_service
from app.schemas import subject
from app.models.user import User


router = APIRouter()


@router.get('/timetables/{timetable_id}/subjects', response_model=List[subject.SubjectResponse])
def fetch_timetable_subjects(request: Request,
                            timetable_id: int,
                            current_user: User = Depends(deps.get_current_active_user),
                            db: Session = Depends(deps.get_db)
                            ):
    
    return subject_service.fetch_timetable_subjects(timetable_id=timetable_id,
                                                 user_id=current_user.id,
                                                 db=db
                                                 )



@router.get('/subjects/{id}', response_model=subject.UniqueSubjectResponse)
def fetch_subject_details(request: Request,
                          id: int,
                          current_user: User = Depends(deps.get_current_active_user),
                          db: Session = Depends(deps.get_db)
                          ):
    
    return subject_service.fetch_subject(user_id=current_user.id,
                                         subject_id=id,
                                         db=db
                                         )


@router.post('/timetables/{timetable_id}/subjects', response_model=subject.UniqueSubjectResponse)
def create_subject(request: Request,
                  timetable_id: int,
                  subject_request: subject.SubjectCreate,
                  current_user: User = Depends(deps.get_current_active_user),
                  db: Session = Depends(deps.get_db)
                  ):
    
    return subject_service.create_subject(subject_request=subject_request,
                                      user_id=current_user.id,
                                      timetable_id=timetable_id,
                                      db=db)


@router.patch('/timetables/{timetable_id}/subjects/{id}', response_model=subject.UniqueSubjectResponse)
def update_subject(timetable_id: int,
                   id: int,
                   request: Request,
                   subject_patch: subject.SubjectUpdate,
                   current_user: User = Depends(deps.get_current_active_user),
                   db: Session = Depends(deps.get_db),
                   ):
    
    return subject_service.update_subject(timetable_id=timetable_id,
                                      user_id=current_user.id,
                                      subject_id=id,
                                      subject_patch=subject_patch,
                                      db=db
                                      )



@router.delete('/subjects/{id}')
def delete_subject(id: int,
                   request: Request,
                   current_user: User = Depends(deps.get_current_active_user),
                    db: Session = Depends(deps.get_db)
                   ):
    
    return subject_service.delete_subject(subject_id=id,
                                      user_id=current_user.id,
                                      db=db
                                      )