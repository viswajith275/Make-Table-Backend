from collections import defaultdict

from app.services.timetable_service.generator import TimeTableGenerator



def apply_assignment_morning_class_days(builder: TimeTableGenerator) -> None:

    for assignment in builder.assignments:

        morning_class_days = getattr(assignment, 'morning_class_days', None)

        if morning_class_days is not None:

            for d in morning_class_days:

                if builder.day_to_index[d] in builder.days:

                    error_msg = f"Morning class double booked for {assignment.teacher.name} at {assignment.class_.class_name} on {d.value}"
                    slack = builder.create_slack(
                        name="assignment morning class days",
                        error_msg=error_msg,
                        weight=10000
                    )

                    builder.model.add(builder.shifts[(assignment.id, builder.day_to_index[d], 1)] + slack >= 1)
