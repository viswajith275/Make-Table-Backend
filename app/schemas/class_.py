from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

class ClassResponse(BaseModel):
    id: int
    class_name: str
    room_name: str
    isLab: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ClassCreate(BaseModel):
    class_name: str
    room_name: str
    isLab: bool = False

    @field_validator('class_name')
    @classmethod
    def class_name_validator(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 25:
            raise ValueError("class name length cannot be greater than 25!")
        return v
    
    @field_validator('room_name')
    @classmethod
    def room_name_validator(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 25:
            raise ValueError("room name length cannot be greater than 25!")
        return v
    
class ClassUpdate(ClassCreate):
    class_name: Optional[str] = None
    room_name: Optional[str] = None
    isLab: Optional[bool] = None