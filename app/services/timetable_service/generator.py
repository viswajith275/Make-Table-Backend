from ortools.sat.python import cp_model
from typing import List


from app.schemas.generation import TeacherAssignmentData
from app.schemas.timetable import TimeTableResponse
# Also import timetable entry model
from app.models.enums import WeekDayEnum, Hardness

class TimeTableGenerator:

    def __init__(self, assignments: List[TeacherAssignmentData], timetable: TimeTableResponse) -> None:

        self.assignments = assignments
        self.slots = range(1,timetable.slots+1)

        self.index_to_day = {i:d for i,d in enumerate(WeekDayEnum)}
        self.day_to_index = {d:i for i,d in enumerate(WeekDayEnum)}

        self.days = set([self.day_to_index[d] for d in timetable.days])

        self.model = cp_model.CpModel()
        self.shifts = {}

        self.hardness_map = {
            Hardness.low: 1,
            Hardness.med: 2,
            Hardness.high: 3
        }
        
        self.slacks = {}
        self.slack_weights = {}
        self.error_msgs = {}

    
    def create_slack(self, name: str, weight: int, error_msg: str, upper_bound: int = 100):
        
        slack_var = self.model.new_int_var(lb=0, ub=upper_bound, name=f"slack_{name}")

        self.slacks[name] = slack_var
        self.slack_weights[name] = weight
        self.error_msgs[name] = error_msg

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