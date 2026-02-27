from pydantic import BaseModel, field_validator, ConfigDict, model_validator
from typing import Optional, List, Self
from datetime import datetime
from app.models.enums import Hardness
from app.schemas.class_ import ClassResponse

class SubjectResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    isLab: bool
    hardness: Hardness

    model_config = ConfigDict(from_attributes=True)

class UniqueSubjectResponse(SubjectResponse):
    min_classes_day: Optional[int] = None
    max_classes_day: Optional[int] = None
    min_classes_week: Optional[int] = None
    max_classes_week: Optional[int] = None
    min_classes_consecutive: Optional[int] = None
    max_classes_consecutive: Optional[int] = None
    lab_classes: Optional[List[ClassResponse]] = None

    model_config = ConfigDict(from_attributes=True)

class SubjectCreate(BaseModel):
    name: str
    min_classes_day: Optional[int] = None
    max_classes_day: Optional[int] = None
    min_classes_week: Optional[int] = None
    max_classes_week: Optional[int] = None
    min_classes_consecutive: Optional[int] = None
    max_classes_consecutive: Optional[int] = None
    isLab: bool = False
    lab_classes: Optional[List[int]] = None
    hardness: Hardness = Hardness.low

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 25:
            raise ValueError("length of subject name cannot be greater than 25!")
        return v
        
    @model_validator(mode='after')
    def validation(self) -> Self:

        if self.isLab == True and (self.lab_classes is None or not self.lab_classes):
            raise ValueError("should choose atleast 1 lab class for a lab subject!")
        
        if self.isLab == False and self.lab_classes is not None:
            raise ValueError("Cannot assign lab classes to a non lab subject!")

        if self.min_classes_day is not None and self.max_classes_day is not None:
            if self.min_classes_day < 1:
                raise ValueError("min classes per day should not be less than 1!")
            
            if self.max_classes_day < 1:
                raise ValueError("max classes per day should not be less than 1!")
            
            if self.min_classes_day > self.max_classes_day:
                raise ValueError("min classes per day should not be greater than max classes per day!")
            
        
        if self.min_classes_week is not None and self.max_classes_week is not None:
            if self.min_classes_week < 1:
                raise ValueError("min classes per week should not be less than 1!")
            
            if self.max_classes_week < 1:
                raise ValueError("max classes per week should not be less than 1!")
            
            if self.min_classes_week > self.max_classes_week:
                raise ValueError("min classes per week should not be greater than max classes per week!")
            
            
        if self.min_classes_consecutive is not None and self.max_classes_consecutive is not None:
            if self.min_classes_consecutive < 1:
                raise ValueError("min consecutive classes should not be less than 1!")
            
            if self.max_classes_consecutive < 1:
                raise ValueError("max consecutive classes should not be less than 1!")
            
            if self.min_classes_consecutive > self.max_classes_consecutive:
                raise ValueError("min consecutive classes should not be greater than max consecutive classes!")
            
        return self

class SubjectUpdate(SubjectCreate):
    name: Optional[str] = None
    isLab: Optional[bool] = None
    hardness: Optional[Hardness] = None
