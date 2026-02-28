from ortools.sat.python import cp_model
from typing import List
from dataclasses import dataclass


from app.schemas.generation import TeacherAssignmentData
from app.schemas.timetable import TimeTableResponse
# Also import timetable entry model
from app.models.enums import WeekDayEnum, Hardness

@dataclass
class SlackTracker():

    variable: cp_model.IntVar
    error_msg: str
    weight: int



class TimeTableGenerator:

    def __init__(self, assignments: List[TeacherAssignmentData], timetable: TimeTableResponse) -> None:

        self.assignments = assignments
        self.slots = range(1,timetable.slots+1)

        self.index_to_day: dict[int, WeekDayEnum] = {i:d for i,d in enumerate(WeekDayEnum)}
        self.day_to_index: dict[WeekDayEnum, int] = {d:i for i,d in enumerate(WeekDayEnum)}

        self.days = set([self.day_to_index[d] for d in timetable.days])

        self.model = cp_model.CpModel()
        self.shifts = {}
        
        # Change values accordingly for better performaces (Dont forget)

        self.hardness_map: dict[Hardness, int] = {
            Hardness.low: 1,
            Hardness.med: 2,
            Hardness.high: 3
        }
        self.distance_weight = 5
        self.max_concern_distance = 3
        
        self.error_slacks: dict[str, SlackTracker] = {}
        self.silent_minimization: list = []

    
    def create_slack(self, name: str, weight: int, error_msg: str, upper_bound: int = 100) -> cp_model.IntVar:
        
        slack_var = self.model.new_int_var(lb=0, ub=upper_bound, name=f"slack_{name}")

        self.error_slacks[name] = SlackTracker(
            variable=slack_var,
            weight=weight,
            error_msg=error_msg
        )

        return slack_var
    
    def create_all_variables(self):

        for assignment in self.assignments:
            for d in self.days:
                for s in self.slots:
                    self.shifts[(assignment.id, d, s)] = self.model.new_bool_var(f"assign_{assignment.id}_d{d}_s{s}")

        return self
    
    # Constraints

    # Future_Note: Change the weights for the constraints according now putting almost all as 10000
    
    # Also add some auto soft condition so that even if the user dont give any value we dont throw a random timetable
    
    def add_teacher_constaints(self):
        
        # Add teacher constraints

        return self
    
    def add_class_constraints(self):

        # Add class constraints

        return self
    
    def add_subject_constraints(self):

        # Add subject constraints

        return self
    
    def add_teacher_assignment_constraints(self):

        # Add teacher assignment constraints

        return self