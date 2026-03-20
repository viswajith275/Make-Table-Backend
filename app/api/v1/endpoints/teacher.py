from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas import teacher
from app.services import teacher_service

router = APIRouter()


@router.get(
    "/timetables/{timetable_id}/teachers", response_model=List[teacher.TeacherResponse]
)
async def fetch_timetable_teachers(
    request: Request,
    timetable_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):

    return await teacher_service.fetch_timetable_teachers(
        timetable_id=timetable_id, user_id=current_user.id, db=db
    )


@router.get("/teachers/{id}", response_model=teacher.UniqueTeacherResponse)
async def fetch_teacher_details(
    request: Request,
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):

    return await teacher_service.fetch_teacher(
        user_id=current_user.id, teacher_id=id, db=db
    )


@router.post(
    "/timetables/{timetable_id}/teachers", response_model=teacher.UniqueTeacherResponse
)
async def create_teacher(
    request: Request,
    timetable_id: int,
    teacher_request: teacher.TeacherCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):

    return await teacher_service.create_teacher(
        teacher_request=teacher_request,
        user_id=current_user.id,
        timetable_id=timetable_id,
        db=db,
    )


@router.patch(
    "/timetables/{timetable_id}/teachers/{id}",
    response_model=teacher.UniqueTeacherResponse,
)
async def update_teacher(
    timetable_id: int,
    id: int,
    request: Request,
    teacher_patch: teacher.TeacherUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):

    return await teacher_service.update_teacher(
        timetable_id=timetable_id,
        user_id=current_user.id,
        teacher_id=id,
        teacher_patch=teacher_patch,
        db=db,
    )


@router.delete("/teachers/{id}")
async def delete_teacher(
    id: int,
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):

    return await teacher_service.delete_teacher(
        teacher_id=id, user_id=current_user.id, db=db
    )
