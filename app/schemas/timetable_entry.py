from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


# Add create update and teacher class subject formating .....
from app.schemas.teacher import TeacherResponse
from app.schemas.class_ import ClassResponse
from app.schemas.subject import SubjectResponse
from app.models.enums import WeekDayEnum, TeacherRole


# Could use a custom made teacher class subject responses schemas
class TimeTableEntryResponse(BaseModel):

    id: int
    slot: int
    subject: SubjectResponse
    lab: Optional[ClassResponse] = None
    teacher_role: TeacherRole

    model_config = ConfigDict(from_attributes=True)

class ClassTimetableEntryResponse(TimeTableEntryResponse):   # Response model for returning class based timetables

    teacher: TeacherResponse

class TeacherTimetableEntryResponse(TimeTableEntryResponse):  # Response model for returning teacher based timetables

    class_: ClassResponse

class ClassFinalEntryResponse(BaseModel):

    day: WeekDayEnum
    entries: List[ClassTimetableEntryResponse]


class TeacherFinalEntryResponse(BaseModel):

    day: WeekDayEnum
    entries: List[TeacherTimetableEntryResponse]

class TimeTableEntryCreate(BaseModel): # The generator function output model also the user create model
    
    slot: int
    day: WeekDayEnum
    teacher_id: int
    class_id: int
    subject_id: int
    lab_id: Optional[int] = None


class TimeTableEntryUpdate(BaseModel):

    slot: Optional[int] = None
    day: Optional[WeekDayEnum] = None

class TimeTableManipulationResponse(TimeTableEntryResponse):

    class_: ClassResponse
    teacher: TeacherResponse