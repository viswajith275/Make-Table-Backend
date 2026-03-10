def apply_assignment_morning_class_days(builder: "TimeTableGenerator") -> None:

    for assignment in builder.assignments:
        morning_class_days = getattr(assignment, "morning_class_days", [])

        if morning_class_days:
            for d in morning_class_days:
                if builder.day_to_index[d] in builder.days:
                    builder.model.add(
                        builder.shifts[(assignment.id, builder.day_to_index[d], 1)] == 1
                    )
