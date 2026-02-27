from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import timetable
from app.api.v1.endpoints import class_
from app.api.v1.endpoints import teacher
from app.api.v1.endpoints import subject
from app.api.v1.endpoints import teacher_assignment

router = APIRouter()

router.include_router(auth.router, tags=["Auth"])
router.include_router(timetable.router, tags=["TimeTable"])
router.include_router(class_.router, tags=["Class"])
router.include_router(teacher.router, tags=["Teacher"])
router.include_router(subject.router, tags=["Subject"])
router.include_router(teacher_assignment.router, tags=["Assignment"])