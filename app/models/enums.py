from enum import Enum

class WeekDayEnum(str, Enum):
    mon = "Mon"
    tue = "Tue"
    wed = "Wed"
    thu = "Thu"
    fri = "Fri"
    sat = "Sat"
    sun = "Sun"

class Hardness(str, Enum):
    low = "Low"
    med = "Med"
    high = "High"

class TeacherRole(str, Enum):
    class_teacher = "Class_Teacher"
    subject_teacher = "Subject_Teacher"

class TimeTableStatus(str, Enum):
    active = "Active"
    pending = "Pending"