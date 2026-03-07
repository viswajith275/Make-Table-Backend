from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.services.timetable_service import timetable_service
from app.schemas import generation
from app.models.user import User


router = APIRouter()



@router.post('/timetable/{timetable_id}/generate', response_model=generation.GenerateResponse)
def create_generation_task(timetable_id: int,
                           request: Request,
                           current_user: User = Depends(deps.get_current_active_user),
                           db: Session = Depends(deps.get_db)
                           ):
    
    return timetable_service.generate_timetable_task(timetable_id=timetable_id,
                                                     user_id=current_user.id,
                                                     db=db)



@router.get('/timetable/{timetable_id}/status', response_model=generation.GenerateResponse)
def check_timetable_status(timetable_id: int,
                           current_user: User = Depends(deps.get_current_active_user),
                           db: Session = Depends(deps.get_db)
                           ):
    
    return timetable_service.current_timetable_status(timetable_id=timetable_id,
                                                      user_id=current_user.id,
                                                      db=db
                                                      )