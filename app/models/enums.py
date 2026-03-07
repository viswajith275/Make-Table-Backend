from enum import Enum

class WeekDayEnum(str, Enum):
    Mon = "Mon"
    Tue = "Tue"
    Wed = "Wed"
    Thu = "Thu"
    Fri = "Fri"
    Sat = "Sat"
    Sun = "Sun"

class Hardness(str, Enum):
    Low = "Low"
    Med = "Med"
    High = "High"

class TeacherRole(str, Enum):
    Class_Teacher = "Class_Teacher"
    Subject_Teacher = "Subject_Teacher"

class TimeTableStatus(str, Enum):
    Active = "Active"
    Processing = "Processing"