from collections import defaultdict


from app.services.timetable_service.generator import TimeTableGenerator


def apply_subject_minimum_daily_limit(builder: TimeTableGenerator) -> None:

    for assignment in builder.assignments:

        min_subject_daily_limit = getattr(assignment.subject, 'min_classes_day', None)

        # Subject should occur atleast specified amount per day

        if min_subject_daily_limit is not None:

            for d in builder.days:

                error_msg = f"Min daily classes does not meet for {assignment.subject.name} on {builder.index_to_day[d].value} (required: {min_subject_daily_limit})"
                slack = builder.create_slack(
                    name="subject minimum classes per day",
                    error_msg=error_msg,
                    weight=10000
                )

                builder.model.add(sum(builder.shifts[(assignment.id, d, s)] for s in builder.slots) + slack>= min_subject_daily_limit)



def apply_subject_maximum_daily_limit(builder: TimeTableGenerator) -> None:

    for assignment in builder.assignments:

        max_subject_daily_limit = getattr(assignment.subject, 'max_classes_day', None)

        # Subject should not occur more than specified amount per day

        if max_subject_daily_limit is not None:

            for d in builder.days:

                error_msg = f"Max daily classes exceeded for {assignment.subject.name} on {builder.index_to_day[d].value} (limit: {max_subject_daily_limit})"
                slack = builder.create_slack(
                    name="subject maximum classes per day",
                    error_msg=error_msg,
                    weight=10000
                )

                builder.model.add(sum(builder.shifts[(assignment.id, d, s)] for s in builder.slots) <= max_subject_daily_limit + slack)



def apply_subject_minimum_weekly_limit(builder: TimeTableGenerator) -> None:

    for assignment in builder.assignments:

        min_subject_weekly_limit = getattr(assignment.subject, 'min_classes_weekly', None)

        # Subject should occur atleast specified amount per week

        if min_subject_weekly_limit is not None:

            error_msg = f"Min weekly classes does not meet for {assignment.subject.name} (required: {min_subject_weekly_limit})"
            slack = builder.create_slack(
                name="subject minimum classes per week",
                error_msg=error_msg,
                weight=10000
            )

            builder.model.add(sum(builder.shifts[(assignment.id, d, s)] for s in builder.slots for d in builder.days) + slack >= min_subject_weekly_limit)