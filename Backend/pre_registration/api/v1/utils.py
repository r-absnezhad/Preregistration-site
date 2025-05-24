def has_completed_prerequisite(profile, course):
    """
    This function checks if a user (profile) has completed all the prerequisite courses for a given course.
    """
    prerequired_courses = course.prerequisite_course.all()
    if not prerequired_courses:
        return True

    for prerequired in prerequired_courses:
        history = profile.course_histories.filter(course=prerequired).first()
        if not history or history.status != "completed":
            return False
