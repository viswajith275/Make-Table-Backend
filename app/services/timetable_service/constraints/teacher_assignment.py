def apply_assignment_morning_class_days(builder: "TimeTableGenerator") -> None:

    for assignment in builder.assignments:
        morning_class_days = getattr(assignment, "morning_class_days", [])

        if morning_class_days:
            for d in morning_class_days:
                if builder.day_to_index[d] in builder.days:
                    builder.model.add(
                        builder.shifts[(assignment.id, builder.day_to_index[d], 1)] == 1
                    )

def apply_all_assignments_should_be_assigned(builder: "TimeTableGenerater") -> None:

    for assignment in builder.assignments:
        error_msg = f"Subject {assignment.subject.name} not assigned to {assignment.class_.class_name} in the timetable"
        slack = builder.create_slack(
            name="subject not assigned",
            error_msg=error_msg,
            weight=250,
        )
        builder.model.add(
            sum(builder.shifts[(assignment.id, d, s)] 
            for d in builder.days
            for s in builder.slots)
            >= 1 - slack
        )