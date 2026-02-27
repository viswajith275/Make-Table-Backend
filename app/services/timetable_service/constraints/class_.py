from collections import defaultdict


from app.services.timetable_service.generator import TimeTableGenerator


def apply_one_teacher_per_slot(builder: TimeTableGenerator) -> None:
        assigned_to_class = defaultdict(list)
        for a in builder.assignments:
            assigned_to_class[a.class_.class_name].append(a)

        # Class should not have 2 teachers at a time

        for class_, class_assignments in assigned_to_class.items():
            
            for d in builder.days:
                for s in builder.slots:

                    error_msg = f"Class conflicts for {class_} at slot {s}"
                    slack = builder.create_slack(
                        name="class conflict",
                        error_msg=error_msg,
                        weight=1000000
                    )

                    builder.model.add(sum(builder.shifts[(assignment.id, d, s)] for assignment in class_assignments) + slack == 1)