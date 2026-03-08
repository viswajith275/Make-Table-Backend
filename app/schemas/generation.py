from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import TeacherRole, TimeTableStatus, WeekDayEnum
from app.schemas.class_ import ClassResponse
from app.schemas.subject import UniqueSubjectResponse
from app.schemas.teacher import UniqueTeacherResponse
from app.schemas.timetable import TimeTableResponse


class GenerateResponse(BaseModel):
    id: int
    status: TimeTableStatus

    model_config = ConfigDict(from_attributes=True)


class GenerateRequest(BaseModel):
    force_timetable: bool = False


class TeacherAssignmentData(BaseModel):
    id: int
    role: TeacherRole
    morning_class_days: Optional[List[WeekDayEnum]] = None

    teacher: UniqueTeacherResponse
    class_: ClassResponse
    subject: UniqueSubjectResponse

    model_config = ConfigDict(from_attributes=True)


class TimeTableCreationData(TimeTableResponse):  # Can write specific validation
    assignments: List[TeacherAssignmentData] = []

    model_config = ConfigDict(from_attributes=True)


class ViolationCreate(BaseModel):
    name: str
    description: str
    severity: int
    violation_amount: int
