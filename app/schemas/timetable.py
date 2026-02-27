from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from app.models.enums import WeekDayEnum

class TimeTableResponse(BaseModel):
    id: int
    name: str
    slots: int
    days: List[WeekDayEnum]
    
    model_config = ConfigDict(from_attributes=True)

class TimeTableCreate(BaseModel):
    name: str
    slots: int
    days: List[WeekDayEnum]

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:

        if v is not None and len(v) > 25:
            raise ValueError("Name cannot be longer than 25 characters!")
        
        return v

    @field_validator('days')
    @classmethod
    def validate_days(cls, v: List[WeekDayEnum] | None) -> List[WeekDayEnum] | None:

        if v is not None and len(v) != len(set(v)):
            raise ValueError("Days cannot contain duplicate values!")
        
        return v
    
    @field_validator('slots')
    @classmethod
    def validate_slots(cls, v: int | None) -> int | None:

        if v  is not None and v < 1:
            raise ValueError("Slots cannot be less than 1!")
        
        return v
    
class TimeTableUpdate(TimeTableCreate):
    name: Optional[str] = None
    slots: Optional[int] = None
    days: Optional[List[WeekDayEnum]] = None