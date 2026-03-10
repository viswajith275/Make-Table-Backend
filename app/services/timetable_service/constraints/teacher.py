from collections import defaultdict


def apply_one_class_per_slot(builder: "TimeTableGenerator") -> None:

    assigned_to_teacher = defaultdict(list)

    for a in builder.assignments:
        assigned_to_teacher[a.teacher.name].append(a)

    # Teacher should take only one class at a time

    for teacher, teacher_assignments in assigned_to_teacher.items():
        for d in builder.days:
            for s in builder.slots:
                builder.model.add(
                    sum(
                        builder.shifts[(assignment.id, d, s)]
                        for assignment in teacher_assignments
                    )
                    <= 1
                )


def apply_teacher_weekly_limit(builder: "TimeTableGenerator") -> None:

    assigned_to_teacher = defaultdict(list)
    for assignment in builder.assignments:
        assigned_to_teacher[assignment.teacher.name].append(assignment)

    for teacher_name, teacher_assignments in assigned_to_teacher.items():
        max_per_week = teacher_assignments[0].teacher.max_classes_day
        if max_per_week is None:
            continue

        error_msg = (
            f"Max weekly classes exceeded {teacher_name} (limit: {max_per_week})"
        )
        slack = builder.create_slack(
            name="teacher weekly limit", error_msg=error_msg, weight=500_000
        )
        builder.model.add(
            sum(
                builder.shifts[(a.id, d, s)]
                for a in teacher_assignments
                for s in builder.slots
                for d in builder.days
            )
            <= max_per_week + slack
        )


def apply_teacher_daily_limit(builder: "TimeTableGenerator") -> None:

    assigned_to_teacher = defaultdict(list)
    for assignment in builder.assignments:
        assigned_to_teacher[assignment.teacher.name].append(assignment)

    for teacher_name, teacher_assignments in assigned_to_teacher.items():
        max_per_day = teacher_assignments[0].teacher.max_classes_day
        if max_per_day is None:
            continue
        for d in builder.days:
            error_msg = (
                f"max weekly classes exceeded {teacher_name} (limit: {max_per_day})"
            )
            slack = builder.create_slack(
                name="teacher daily limit", error_msg=error_msg, weight=500_000
            )
            builder.model.add(
                sum(
                    builder.shifts[(a.id, d, s)]
                    for a in teacher_assignments
                    for s in builder.slots
                )
                <= max_per_day + slack
            )


def apply_teacher_consecutive_limit(builder: "TimeTableGenerator") -> None:

    assigned_to_teacher = defaultdict(list)

    for assignment in builder.assignments:
        if getattr(assignment.teacher, "max_classes_consecutive", None) is not None:
            assigned_to_teacher[
                (assignment.teacher.name, assignment.teacher.max_classes_consecutive)
            ].append(assignment)

    # Teacher should not take more consecutive classes than specified

    for teacher, teacher_assignments in assigned_to_teacher.items():
        max_consecutive_classes_per_day = teacher[1]

        for d in builder.days:
            combined_slots_of_teacher = []

            for s in builder.slots:
                slotes_at_s = [
                    builder.shifts[assignment.id, d, s]
                    for assignment in teacher_assignments
                ]

                combined_slots_of_teacher.append(sum(slotes_at_s))

            for i in range(
                len(combined_slots_of_teacher) - max_consecutive_classes_per_day
            ):
                error_msg = f"Max consecutive classes exceed {teacher[0]} (limit: {max_consecutive_classes_per_day})"
                slack = builder.create_slack(
                    name="teacher consecutive limit",
                    error_msg=error_msg,
                    weight=500_000,
                )

                builder.model.add(
                    sum(
                        combined_slots_of_teacher[
                            i : i + max_consecutive_classes_per_day + 1
                        ]
                    )
                    <= max_consecutive_classes_per_day + slack
                )
