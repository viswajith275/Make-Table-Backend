from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


# Add create update and teacher class subject formating .....
from app.schemas.teacher import TeacherResponse
from app.schemas.class_ import ClassResponse
from app.schemas.subject import SubjectResponse
from app.models.enums import WeekDayEnum, TeacherRole

# Could use a custom made teacher class subject responses schemas
class TimeTableEntryBase(BaseModel):

    id: int
    slot: int
    day: WeekDayEnum
    subject: SubjectResponse
    lab: Optional[ClassResponse] = None
    role: TeacherRole

    model_config = ConfigDict(from_attributes=True)

class TimeTableEntryResponse(TimeTableEntryBase):

    teacher: TeacherResponse
    class_: ClassResponse

    model_config = ConfigDict(from_attributes=True)

class TimeTableEntryCreate(BaseModel): # The generator function output model also the user create model
    
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

