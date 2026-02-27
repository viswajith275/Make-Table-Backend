from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.services import class_service
from app.schemas import class_
from app.models.user import User


router = APIRouter()


@router.get('/timetables/{timetable_id}/classes', response_model=List[class_.ClassResponse])
def fetch_timetable_classes(request: Request,
                            timetable_id: int,
                            current_user: User = Depends(deps.get_current_active_user),
                            db: Session = Depends(deps.get_db)
                            ):
    
    return class_service.fetch_timetable_classes(timetable_id=timetable_id,
                                                 user_id=current_user.id,
                                                 db=db
                                                 )


@router.post('/timetables/{timetable_id}/classes', response_model=class_.ClassResponse)
def create_class(request: Request,
                 timetable_id: int,
                 class_request: class_.ClassCreate,
                 current_user: User = Depends(deps.get_current_active_user),
                db: Session = Depends(deps.get_db)
                ):
    
    return class_service.create_class(class_request=class_request,
                                      user_id=current_user.id,
                                      timetable_id=timetable_id,
                                      db=db)


@router.patch('/timetables/{timetable_id}/classes/{id}', response_model=class_.ClassResponse)
def update_class(timetable_id: int,
                   id: int,
                   request: Request,
                   class_patch: class_.ClassUpdate,
                   current_user: User = Depends(deps.get_current_active_user),
                   db: Session = Depends(deps.get_db),
                   ):
    
    return class_service.update_class(timetable_id=timetable_id,
                                      user_id=current_user.id,
                                      class_id=id,
                                      class_patch=class_patch,
                                      db=db
                                      )



@router.delete('/classes/{id}')
def delete_class(id: int,
                   request: Request,
                   current_user: User = Depends(deps.get_current_active_user),
                    db: Session = Depends(deps.get_db)
                   ):
    
    return class_service.delete_class(class_id=id,
                                      user_id=current_user.id,
                                      db=db
                                      )