from collections import defaultdict


from app.services.timetable_service.generator import TimeTableGenerator

def apply_one_class_per_slot(builder: TimeTableGenerator) -> None:

    assigned_to_teacher = defaultdict(list)

    for a in builder.assignments:
        assigned_to_teacher[a.teacher.name].append(a)

        # Teacher should take only one class at a time

        for teacher, teacher_assignments in assigned_to_teacher.items():

            for d in builder.days:
                for s in builder.slots:

                    error_msg = f"Teacher conflicts for {teacher} at slot {s}"
                    slack = builder.create_slack(
                        name="teacher conflict",
                        error_msg=error_msg,
                        weight=1000000
                    )

                    builder.model.add(sum(builder.shifts[(assignment.id, d, s)] for assignment in teacher_assignments) + slack == 1)


def apply_teacher_weekly_limit(builder: TimeTableGenerator) -> None:

        for assignment in builder.assignments:

            max_classes_per_week = getattr(assignment.teacher, 'max_classes_week', None)

            # Teacher should not take more than the weekly limit

            if max_classes_per_week is not None:

                error_msg = f"Max weekly classes exceeded {assignment.teacher.name} (limit: {max_classes_per_week})"
                slack = builder.create_slack(
                    name="teacher weekly limit",
                    error_msg=error_msg,
                    weight=10000
                )

                builder.model.add(sum(builder.shifts[(assignment.id, d, s)] for s in builder.slots for d in builder.days) <= max_classes_per_week + slack)


def apply_teacher_daily_limit(builder: TimeTableGenerator) -> None:
     
     for assignment in builder.assignments:
          
        max_class_per_day = getattr(assignment.teacher, 'max_classes_day', None)
        
        # TEacher should not take more than the daily limit

        if max_class_per_day is not None:

            for d in builder.days:
               
                error_msg = f"max weekly classes exceeded {assignment.teacher.name} (limit: {max_class_per_day})"
                slack = builder.create_slack(
                        name='teacher daily limit',
                        error_msg=error_msg,
                        weight=10000
                )

                builder.model.add(sum(builder.shifts[(assignment.id, d, s)] for s in builder.slots) <= max_class_per_day + slack)


def apply_teacher_consecutive_limit(builder: TimeTableGenerator) -> None:

    assigned_to_teacher = defaultdict(list)

    for assignment in builder.assignments:

        if getattr(assignment.teacher, 'max_classes_consecutive', None) is not None:

            assigned_to_teacher[assignment.teacher].append(assignment)

    # Teacher should not take more consecutive classes than specified

    for teacher, teacher_assignments in assigned_to_teacher.items():

        max_consecutive_classes_per_day = teacher.max_classes_consecutive

        for d in builder.days:

            combined_slots_of_teacher = []

            for s in builder.slots:

                slotes_at_s = [builder.shifts[assignment.id, d, s] for assignment in teacher_assignments]

                combined_slots_of_teacher.append(sum(slotes_at_s))

            for i in range(len(combined_slots_of_teacher) - max_consecutive_classes_per_day):

                error_msg = f"Max consecutive classes exceed {teacher.name} (limit: {max_consecutive_classes_per_day})"
                slack = builder.create_slack(
                    name='teacher consecutive limit',
                    error_msg=error_msg,
                    weight=10000
                )

                builder.model.add(sum(combined_slots_of_teacher[i: i + max_consecutive_classes_per_day + 1]) <= max_consecutive_classes_per_day + slack)