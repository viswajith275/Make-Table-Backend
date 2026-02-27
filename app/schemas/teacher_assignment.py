from pydantic import BaseModel, field_validator, ConfigDict, model_validator
from typing import Optional, List
from datetime import datetime
from app.models.enums import TeacherRole, WeekDayEnum, Hardness

class ClassDetail(BaseModel):
    class_name: str
    room_name: str

    model_config = ConfigDict(from_attributes=True)

class SubjectDetail(BaseModel):
    name: str
    hardness: Hardness

    model_config = ConfigDict(from_attributes=True)

class TeacherAssignmentResponse(BaseModel):

    id: int
    created_at: datetime
    class_: ClassDetail
    subject: SubjectDetail
    role: TeacherRole
    morning_class_days: Optional[List[WeekDayEnum]]

    model_config = ConfigDict(from_attributes=True)

class TeacherAssignmentCreate(BaseModel):

    teacher_id: int
    class_id: int
    subject_id: int
    role: TeacherRole = TeacherRole.subject_teacher
    morning_class_days: Optional[List[WeekDayEnum]] = None

    @field_validator('morning_class_days')
    @classmethod
    def validate_days(cls, v: List[WeekDayEnum] | None) -> List[WeekDayEnum] | None:

        if v is not None and len(v) != len(set(v)):
            raise ValueError("Days cannot contain duplicate values!")
        
        return v
    
class TeacherAssignmentUpdate(BaseModel):
    role: Optional[TeacherRole] = None
    morning_class_days: Optional[List[WeekDayEnum]] = None

    @field_validator('morning_class_days')
    @classmethod
    def validate_days(cls, v: List[WeekDayEnum]) -> List[WeekDayEnum]:

        if len(v) != len(set(v)):
            raise ValueError("Days cannot contain duplicate values!")
        
        return v