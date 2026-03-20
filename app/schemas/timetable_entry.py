from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import TeacherRole, WeekDayEnum
from app.schemas.class_ import ClassResponse
from app.schemas.subject import SubjectResponse

# Add create update and teacher class subject formating .....
from app.schemas.teacher import TeacherResponse


# Could use a custom made teacher class subject responses schemas
class TimeTableEntryBase(BaseModel):
    id: int
    slot: int
    day: WeekDayEnum
    subject: SubjectResponse
    lab: Optional[ClassResponse] = None
    role: TeacherRole

    model_config = ConfigDict(from_attributes=True)


class TeacherTimeTableEntryResponse(TimeTableEntryBase):
    class_: ClassResponse

    model_config = ConfigDict(from_attributes=True)


class ClassTimeTableEntryResponse(TimeTableEntryBase):
    teacher: TeacherResponse

    model_config = ConfigDict(from_attributes=True)


class TimeTableEntryCreate(
    BaseModel
):  # The generator function output model also the user create model
    slot: int
    day: WeekDayEnum
    teacher_id: int
    class_id: int
    subject_id: int
    lab_id: Optional[int] = None
    role: TeacherRole


class TimeTableEntryUpdate(BaseModel):
    slot: Optional[int] = None
    day: Optional[WeekDayEnum] = None
