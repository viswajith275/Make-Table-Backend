from fastapi import APIRouter, Request, Depends, Query
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
                           force_generation: bool = Query(default=False, description="Force generation by ignoring the constraints!"),
                           current_user: User = Depends(deps.get_current_active_user),
                           db: Session = Depends(deps.get_db)
                           ):
    
    return timetable_service.generate_timetable_task(timetable_id=timetable_id,
                                                     user_id=current_user.id,
                                                     db=db,
                                                     force_generation=force_generation
                                                     )



@router.get('/timetable/{timetable_id}/status', response_model=generation.GenerateResponse)
def check_timetable_status(timetable_id: int,
                           current_user: User = Depends(deps.get_current_active_user),
                           db: Session = Depends(deps.get_db)
                           ):
    
    return timetable_service.current_timetable_status(timetable_id=timetable_id,
                                                      user_id=current_user.id,
                                                      db=db
                                                      )