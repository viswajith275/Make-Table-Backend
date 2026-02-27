from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.services.timetable_service import timetable_service
from app.schemas import timetable
from app.models.user import User


router = APIRouter()


@router.get('/timetables', response_model=List[timetable.TimeTableResponse])
def fetch_all_timetables(request: Request,
                         current_user: User = Depends(deps.get_current_active_user),
                          db: Session = Depends(deps.get_db)
                          ):

    return timetable_service.fetch_all_timetables(user_id=current_user.id,
                                                   db=db)


@router.post('/timetables', response_model=timetable.TimeTableResponse)
def create_timetable(request: Request,
                     timetable_request: timetable.TimeTableCreate,
                     current_user: User = Depends(deps.get_current_active_user),
                     db: Session = Depends(deps.get_db)
                     ):
    
    return timetable_service.create_timetable(user_id=current_user.id,
                                              timetable_request=timetable_request,
                                              db=db
                                              )


@router.patch('/timetables/{id}', response_model=timetable.TimeTableResponse)
def update_timetable(request: Request,
                     id: int,
                     timetable_patch: timetable.TimeTableUpdate,
                     current_user: User = Depends(deps.get_current_active_user),
                     db: Session = Depends(deps.get_db)
                     ):
    
    return timetable_service.update_timetable(timetable_id=id,
                                              timetable_patch=timetable_patch,
                                              user_id=current_user.id,
                                              db=db
                                              )


@router.delete('/timetables/{id}')
def delete_timetable(request: Request,
                     id: int,
                     current_user: User = Depends(deps.get_current_active_user),
                     db: Session = Depends(deps.get_db)
                     ):
    
    return timetable_service.delete_timetable(timetable_id=id,
                                              user_id=current_user.id,
                                              db=db
                                              )