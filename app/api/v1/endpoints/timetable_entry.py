from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.core.rate_limiter import limiter
from app.schemas import timetable_entry
from app.services import timetable_entry_service

router = APIRouter()


@router.get(
    "/classes/{class_id}/entries",
    response_model=timetable_entry.ClassEntryResponse,
)
async def fetch_class_timetable_entries(
    request: Request,
    class_id: int,
    current_user: User | None = Depends(deps.get_current_active_optional_user),
    db: AsyncSession = Depends(deps.get_db),
):

    return await timetable_entry_service.fetch_class_entries(
        class_id=class_id, user_id= None if current_user is None else current_user.id, db=db
    )


@router.get(
    "/teacher/{teacher_id}/entries",
    response_model=timetable_entry.TeacherEntryResponse,
)
async def fetch_teacher_timetable_entries(
    request: Request,
    teacher_id: int,
    current_user: User | None = Depends(deps.get_current_active_optional_user),
    db: AsyncSession = Depends(deps.get_db),
):

    return await timetable_entry_service.fetch_teacher_entries(
        teacher_id=teacher_id, user_id= None if current_user is None else current_user.id, db=db
    )
