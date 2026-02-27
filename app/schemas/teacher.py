from pydantic import BaseModel, field_validator, ConfigDict, model_validator
from typing import Optional, List, Self
from datetime import datetime

class TeacherResponse(BaseModel):
    id: int
    name: str
    
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UniqueTeacherResponse(TeacherResponse):
    max_classes_day: Optional[int] = None
    max_classes_week: Optional[int] = None
    max_classes_consecutive: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class TeacherCreate(BaseModel):
    name: str
    max_classes_day: Optional[int] = None
    max_classes_week: Optional[int] = None
    max_classes_consecutive: Optional[int] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 25:
            raise ValueError("length teacher name should not be greater than 25!")
        return v
    
    @model_validator(mode='after')
    def validate_properties(self) -> Self:

        if self.max_classes_week is not None and self.max_classes_week < 1:
            raise ValueError("max_classes_week must be greater than 1!")
        
        if self.max_classes_consecutive is not None and self.max_classes_consecutive < 1:
            raise ValueError("max_classes_consecutive must be greater than 1!")
        
        if self.max_classes_day is not None and self.max_classes_day < 1:
            raise ValueError("max_classes_day must be greater than 1!")
        
        return self
    
class TeacherUpdate(TeacherCreate):
    name: Optional[str] = None
    max_classes_day: Optional[int] = None
    max_classes_week: Optional[int] = None
    max_classes_consecutive: Optional[int] = None

