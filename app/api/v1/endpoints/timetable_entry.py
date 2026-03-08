from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas import timetable_entry
from app.services import timetable_entry_service

router = APIRouter()


@router.get(
    "/classes/{class_id}/entries", response_model=timetable_entry.TimeTableEntryBase
)
def get_timetable_entries_class(
    request: Request,
    class_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    return timetable_entry_service.fetch_class_entries(
        class_id=class_id, user_id=current_user.id, db=db
    )


@router.get(
    "/teacher/{teacher_id}/entries",
    response_model=timetable_entry.TimeTableEntryResponse,
)
def get_timetable_entries_teacher(
    request: Request,
    teacher_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    return timetable_entry_service.fetch_teacher_entries(
        teacher_id=teacher_id, user_id=current_user.id, db=db
    )
