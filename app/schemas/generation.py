from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any


from app.schemas.teacher import UniqueTeacherResponse
from app.schemas.class_ import ClassResponse
from app.schemas.subject import UniqueSubjectResponse
from app.models.enums import WeekDayEnum, TeacherRole, TimeTableStatus


class GenerateResponse(BaseModel):
    status: TimeTableStatus
    error: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class GenerateRequest(BaseModel):
    force_timetable: bool = False


class TeacherAssignmentData(BaseModel):
    id: int
    role: TeacherRole
    morning_class_days: List[WeekDayEnum]

    teacher: UniqueTeacherResponse
    class_: ClassResponse
    subject: UniqueSubjectResponse

    model_config = ConfigDict(from_attributes=True)