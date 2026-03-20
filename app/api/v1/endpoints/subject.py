from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas import subject
from app.services import subject_service

router = APIRouter()


@router.get(
    "/timetables/{timetable_id}/subjects", response_model=List[subject.SubjectResponse]
)
async def fetch_timetable_subjects(
    request: Request,
    timetable_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):

    return await subject_service.fetch_timetable_subjects(
        timetable_id=timetable_id, user_id=current_user.id, db=db
    )


@router.get("/subjects/{id}", response_model=subject.UniqueSubjectResponse)
async def fetch_subject_details(
    request: Request,
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):

    return await subject_service.fetch_subject(
        user_id=current_user.id, subject_id=id, db=db
    )


@router.post(
    "/timetables/{timetable_id}/subjects", response_model=subject.UniqueSubjectResponse
)
async def create_subject(
    request: Request,
    timetable_id: int,
    subject_request: subject.SubjectCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):

    return await subject_service.create_subject(
        subject_request=subject_request,
        user_id=current_user.id,
        timetable_id=timetable_id,
        db=db,
    )


@router.patch(
    "/timetables/{timetable_id}/subjects/{id}",
    response_model=subject.UniqueSubjectResponse,
)
async def update_subject(
    timetable_id: int,
    id: int,
    request: Request,
    subject_patch: subject.SubjectUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):

    return await subject_service.update_subject(
        timetable_id=timetable_id,
        user_id=current_user.id,
        subject_id=id,
        subject_patch=subject_patch,
        db=db,
    )


@router.delete("/subjects/{id}")
async def delete_subject(
    id: int,
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):

    return await subject_service.delete_subject(
        subject_id=id, user_id=current_user.id, db=db
    )
