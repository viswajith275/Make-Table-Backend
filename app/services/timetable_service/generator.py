from ortools.sat.python import cp_model
from typing import List, Tuple
from collections import defaultdict
from dataclasses import dataclass
from random import randint


from app.schemas.generation import TimeTableCreationData, ViolationCreate, TeacherAssignmentData
from app.schemas.timetable_entry import TimeTableEntryCreate
from app.models.enums import WeekDayEnum, Hardness
from app.services.timetable_service.constraints import teacher, class_, teacher_assignment, subject


@dataclass
class SlackTracker():

    variable: cp_model.IntVar
    error_msg: str
    weight: int


class TimeTableGenerator:

    def __init__(self, timetable_data: TimeTableCreationData) -> None:

        self.assignments = timetable_data.assignments
        self.id_to_assignment_map: dict[int, TeacherAssignmentData] = {a.id: a for a in self.assignments }
        self.slots = range(1,timetable_data.slots+1)

        self.index_to_day: dict[int, WeekDayEnum] = {i:d for i,d in enumerate(WeekDayEnum)}
        self.day_to_index: dict[WeekDayEnum, int] = {d:i for i,d in enumerate(WeekDayEnum)}

        self.days = set([self.day_to_index[d] for d in timetable_data.days])


        self.model = cp_model.CpModel()
        self.shifts = {}
        
        # Change values accordingly for better performaces (Dont forget)

        self.hardness_map: dict[Hardness, int] = {
            Hardness.Low: 1,
            Hardness.Med: 2,
            Hardness.High: 3
        }
        self.distance_weight: int = 5
        self.max_concern_distance: int = 3
        self.weight: int = 50000
        
        self.error_slacks: dict[str, SlackTracker] = {}
        self.silent_minimization: list = []

    
    def create_slack(self, name: str, weight: int, error_msg: str, upper_bound: int = 100) -> cp_model.IntVar:
        
        slack_var: cp_model.IntVar = self.model.new_int_var(lb=0, ub=upper_bound, name=f"slack_{name}")

        self.error_slacks[name] = SlackTracker(
            variable=slack_var,
            weight=weight,
            error_msg=error_msg
        )

        return slack_var
    
    def create_all_shifts(self):

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

        teacher.apply_one_class_per_slot(self)
        teacher.apply_teacher_daily_limit(self)
        teacher.apply_teacher_weekly_limit(self)
        teacher.apply_teacher_consecutive_limit(self)

        return self
    
    def add_class_constraints(self):

        # Add class constraints

        class_.apply_one_teacher_per_slot(self)

        return self
    
    def add_subject_constraints(self):

        # Add subject constraints
        
        subject.apply_subject_minimum_daily_limit(self)
        subject.apply_subject_maximum_daily_limit(self)
        subject.apply_subject_minimum_weekly_limit(self)
        subject.apply_subject_maximum_weekly_limit(self)
        subject.apply_subject_minimum_consecutive_limit(self)
        subject.apply_subject_maximum_consecutive_limit(self)
        subject.apply_subject_hardness(self)
        subject.apply_hard_subject_distances(self)

        return self
    
    def add_teacher_assignment_constraints(self):

        # Add teacher assignment constraints

        teacher_assignment.apply_assignment_morning_class_days(self)

        return self
    
    # Maximising every shift that timetable feel filled

    def maximize_allocation_of_assignment(self):

        all_shifts = [self.shifts[(assignment.id, d, s)]
                           for assignment in self.assignments
                           for d in self.days
                           for s in self.slots
                           ]
        
        self.silent_minimization.append(sum(all_shifts) * -self.weight)

        return self
    
    # Set objective and set up the solver

    def minimize_and_compile(self):

        all_shifts: list = self.silent_minimization

        for slack in self.error_slacks.values():

            all_shifts.append(slack.variable * slack.weight)

        self.model.minimize(sum(all_shifts))

        return self
    

    def solve_and_generate(self) -> tuple[List[TimeTableEntryCreate], List[ViolationCreate]]:

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30
        solver.parameters.num_search_workers = 8
        solver.parameters.random_polarity_ratio = 0.99  # 99% chance to choose 0 or 1 randomly
        solver.parameters.random_seed = randint(0, 10000)

        status = solver.Solve(self.model)

        timetable: List[TimeTableEntryCreate] = []
        violations: List[ViolationCreate] = []

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):

            for name, slack in self.error_slacks.items():

                slack_val = solver.value(slack.variable)

                if slack_val > 0:
                    violations.append(
                        ViolationCreate(
                            name=name,
                            description=slack.error_msg,
                            severity=slack.weight,
                            violation_amount=slack_val
                        )
                    )

            busy_rooms = defaultdict(set)

            for (a_id, day, slot), var in self.shifts.items():

                assignment = self.id_to_assignment_map[a_id]

                if solver.value(var):

                    lab_class_id = None

                    if assignment.subject.lab_classes:

                        availdable_classes = assignment.subject.lab_classes

                        for class_ in availdable_classes:

                            if class_.id not in busy_rooms[(day, slot)]:
                                lab_class_id = class_.id
                                busy_rooms[(day, slot)].add(class_.id)
                                break

                    timetable.append(
                        TimeTableEntryCreate(
                            slot=slot,
                            day=self.index_to_day[day],
                            teacher_id=assignment.teacher.id,
                            class_id=assignment.class_.id,
                            subject_id=assignment.subject.id,
                            lab_id=lab_class_id
                        )
                    )

        # Handle timetable model down condition

        return timetable, violations