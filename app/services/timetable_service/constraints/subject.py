from collections import defaultdict


from app.services.timetable_service.generator import TimeTableGenerator


def apply_subject_minimum_daily_limit(builder: TimeTableGenerator) -> None:

    for assignment in builder.assignments:

        min_subject_daily_val = getattr(assignment.subject, 'min_classes_day', None)

        # Subject should occur atleast specified amount per day

        if min_subject_daily_val is not None:

            for d in builder.days:

                error_msg = f"Min daily classes does not meet for {assignment.subject.name} on {builder.index_to_day[d].value} (required: {min_subject_daily_val}"
                slack = builder.create_slack(
                    name="subject minimum classes per day",
                    error_msg=error_msg,
                    weight=10000
                )

                builder.model.add(sum(builder.shifts[(assignment.id, d, s)] for s in builder.slots) + slack >= min_subject_daily_val)



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

        min_subject_weekly_val = getattr(assignment.subject, 'min_classes_weekly', None)

        # Subject should occur atleast specified amount per week

        if min_subject_weekly_val is not None:

            error_msg = f"Min weekly classes does not meet for {assignment.subject.name} (required: {min_subject_weekly_val})"
            slack = builder.create_slack(
                name="subject minimum classes per week",
                error_msg=error_msg,
                weight=10000
            )

            builder.model.add(sum(builder.shifts[(assignment.id, d, s)] for s in builder.slots for d in builder.days) + slack >= min_subject_weekly_val)



def apply_subject_maximum_weekly_limit(builder: TimeTableGenerator) -> None:

    for assignment in builder.assignments:

        max_subject_weekly_limit = getattr(assignment.subject, 'max_classes_weekly', None)

        # Subject should not occur more than specified amount per week

        if max_subject_weekly_limit is not None:

            error_msg = f"Max weekly limit for {assignment.subject.name} (limit: {max_subject_weekly_limit})"
            slack = builder.create_slack(
                name="subject maximum classes per week",
                error_msg=error_msg,
                weight=10000
            )

            builder.model.add(sum(builder.shifts[(assignment.id, d, s)] for s in builder.slots for d in builder.days) <= max_subject_weekly_limit + slack)



def apply_subject_minimum_consecutive_limit(builder: TimeTableGenerator) -> None:

    for assignment in builder.assignments:

        min_subject_consecutive_val = getattr(assignment.subject, 'min_classes_consecuive', None)

        # Subject should not consecutively taken more than specified amount per day

        if min_subject_consecutive_val is not None:

            for d in builder.days:

                total_slots_per_day = [builder.shifts[(assignment.id, d, s)] for s in builder.slots]
                no_of_slotes = len(total_slots_per_day)

                if min_subject_consecutive_val == 2:

                    for i, cur_slot in enumerate(total_slots_per_day):

                        neighbours = []

                        if i > 0:
                            neighbours.append(total_slots_per_day[i-1])

                        if i < no_of_slotes-1:
                            neighbours.append(total_slots_per_day[i+1])

                        if neighbours:

                            error_msg = f"Single class for {assignment.subject.name} in {assignment.class_.class_name} on {builder.index_to_day[d].value} slot {i + 1} (required: 2)"
                            slack = builder.create_slack(
                                name="subject single class",
                                error_msg=error_msg,
                                weight=10000
                            )

                            builder.model.add(sum(neighbours) + slack >= 1).only_enforce_if(cur_slot)
                        
                        else:

                            error_msg = f"Imposible consecutive class {assignment.subject.name} in {assignment.class_.class_name} on {builder.index_to_day[d].value}"
                            slack = builder.create_slack(
                                name="subject impossible for consecutive class",
                                error_msg=error_msg,
                                weight=10000
                            )

                            builder.model.add(slack >= 1).only_enforce_if(cur_slot)

                
                else:

                    needed_consecutive_class = min_subject_consecutive_val - 1

                    for s, cur_slot in enumerate(total_slots_per_day):

                        is_start = builder.model.new_bool_var(f'start_{assignment.id}_{d}_{s}') # For checking if the cur_slot is starting of consecutive sequence

                        if s > 0:

                            prev = total_slots_per_day[s-1]

                            builder.model.add_bool_and([cur_slot, prev.Not()]).only_enforce_if(is_start)
                            builder.model.add_bool_or([cur_slot.Not(), prev]).only_enforce_if(is_start.Not())
                        
                        else:

                            builder.model.add(is_start == cur_slot)

                        has_room_for_classes = (s + needed_consecutive_class) < no_of_slotes

                        if has_room_for_classes:

                            for i in range(needed_consecutive_class):

                                error_msg = f"Consecutive sequence broken for {assignment.subject.name} in {assignment.class_.class_name} on {builder.index_to_day[d].value}"
                                slack = builder.create_slack(
                                    name="subject consecutive sequence broken",
                                    error_msg=error_msg,
                                    weight=10000
                                )

                                builder.model.add(total_slots_per_day[s + i] + slack >= 1).only_enforce_if(is_start)

                        else:

                            error_msg = f"Not enough slots to complete consecutive limit for {assignment.subject.name} in {assignment.class_.class_name} on {builder.index_to_day[d].value}"
                            slack = builder.create_slack(
                                name="subject not enough slots",
                                error_msg=error_msg,
                                weight=10000
                            )

                            builder.model.add(slack >= 1).only_enforce_if(is_start)



def apply_subject_maximum_consecutive_limit(builder: TimeTableGenerator) -> None:

    for assignment in builder.assignments:

        max_subeject_consecutive_limit = getattr(assignment.subject, 'max_classes_consecutive', None)

        # Subject should not consecutively occur more than specified amount per day

        if max_subeject_consecutive_limit is not None:

            for d in builder.days:

                total_slots_per_day = [builder.shifts[(assignment.id, d, s)] for s in builder.slots]
                
                for i in range(len(total_slots_per_day) - max_subeject_consecutive_limit):

                    error_msg = f"Max consecutive classes exceeded for {assignment.subject.name} in {assignment.class_.class_name} on {builder.index_to_day[d].value} (limit: {max_subeject_consecutive_limit})"
                    slack = builder.create_slack(
                        name="subject maximum consecutive class",
                        error_msg=error_msg,
                        weight=10000
                    )

                    builder.model.add(sum(total_slots_per_day[i: i + max_subeject_consecutive_limit + 1]) <= max_subeject_consecutive_limit + slack)



# Actually a class constraint (Dont know if there is a better way to write this)

def apply_subject_per_lab(builder: TimeTableGenerator) -> None:

    assigned_to_lab_class = defaultdict(list)

    for assignment in builder.assignments:

        is_lab_subject = getattr(assignment.subject, 'isLab', False)
        lab_classes = getattr(assignment.subject, 'lab_classes', [])

        if is_lab_subject:

            for c in lab_classes:

                assigned_to_lab_class[c.class_name].append(assignment)

    for class_, class_assignments in assigned_to_lab_class.items():

        if len(class_assignments) < 2:
            continue

        for d in builder.days:
            for s in builder.slots:

                error_msg = f"Lab class conflict of {class_} on {builder.index_to_day[d]}"
                slack = builder.create_slack(
                    name="lab conflicts",
                    error_msg=error_msg,
                    weight=10000
                )

                builder.model.add(sum(builder.shifts[(assignment.id, d, s)] for assignment in class_assignments) <= 1 + slack)




def apply_subject_hardness(builder: TimeTableGenerator) -> None:

    # Applying that hard subjects appear earlier than easy subjects

    slot_cost = {s: (s-1) ** 2 for s in builder.slots}

    builder.silent_minimization.extend(
        builder.shifts[(assignment.id, d, s)] * slot_cost[s] * builder.hardness_map[assignment.subject.hardness]
        for s in builder.slots
        for d in builder.days
        for assignment in builder.assignments
        )



def apply_hard_subject_distances(builder: TimeTableGenerator) -> None:

    # Maximizing the distance between 2 hard subjects so that all hard subject dont clutter around morning times

    hard_subjects = [assignment for assignment in builder.assignments if assignment.subject.hardness.value == "High" and getattr(assignment.subject, "min_classes_consecutive", 0) < 2]

    for d in builder.days:
        for i, a1 in enumerate(hard_subjects):
            for a2 in hard_subjects[i+1:]:
                for s1 in builder.slots:
                    for s2 in builder.slots:

                        if s1 >= s2 or abs(s2 - s1) > builder.max_concern_distance:
                            continue

                        
                        distance = s2 - s1
                        max_distance = len(builder.slots) - 1
                        proximity_cost = (max_distance - distance) * builder.distance_weight

                        if proximity_cost == 0:
                            continue

                        both_scheduled = builder.model.new_bool_var(f'both_{a1.id}_{a2.id}_{d}_{s1}_{s2}')
                        builder.model.add_min_equality(both_scheduled, [
                            builder.shifts[(a1.id, d, s1)],
                            builder.shifts[(a2.id, d, s2)]
                        ])

                        builder.silent_minimization.append(both_scheduled * proximity_cost)
