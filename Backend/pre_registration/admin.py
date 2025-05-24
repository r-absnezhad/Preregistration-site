from django.contrib import admin
from .models import Registrations, Course, Category, CourseHistory


# Register your models here.
class CourseHistoryAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the CourseHistory model.
    - Displays the username, course, prerequisite status, and status of the course history.
    - Allows filtering, searching, and autocomplete for related fields.
    """

    list_display = ("get_username", "course", "get_prerequisite_status", "status")
    list_filter = ("status",)
    search_fields = ("profile__user__username", "course__name")
    autocomplete_fields = ("profile", "course")

    def get_username(self, obj):
        return obj.profile.user.username

    get_username.short_description = "Username"

    def get_prerequisite_status(self, obj):
        prerequisite_courses = obj.course.prerequisite_course.all()
        if not prerequisite_courses:
            return "No prerequisite"

        # check prerequisite courses
        completed_courses = obj.profile.course_histories.filter(
            course__in=prerequisite_courses, status="completed"
        ).values_list("course", flat=True)
        failed_courses = obj.profile.course_histories.filter(
            course__in=prerequisite_courses, status="failed"
        ).exists()

        if (
            set(prerequisite_courses.values_list("id", flat=True))
            == set(completed_courses)
            and not failed_courses
        ):
            return "Prerequisite completed"
        elif failed_courses:
            return "Prerequisite failed"
        else:
            return "Prerequisite not completed"

    get_prerequisite_status.short_description = "Prerequisite Status"


admin.site.register(CourseHistory, CourseHistoryAdmin)


class RegistrationsAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the Registrations model.
    - Displays the term and username of the user who made the registration.
    - Allows filtering, searching, and ordering by user ID and term.
    """

    list_display = ["term", "get_username"]
    list_filter = ["term", "user_id"]
    search_fields = ["term"]
    ordering = ["term", "user_id"]

    def get_username(self, obj):
        return obj.user_id.user.username

    get_username.short_description = "Username"


admin.site.register(Registrations, RegistrationsAdmin)


class CourseAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the Course model.
    - Displays the course ID, name, credit, category, and whether it has a prerequisite.
    - Allows filtering, searching, and ordering by course attributes.
    """

    list_display = [
        "id",
        "name",
        "credit",
        "get_category_name",
        "have_prerequisite_course",
    ]
    list_filter = ["name", "credit", "have_prerequisite_course", "category__name"]
    search_fields = ["name"]
    ordering = ["id", "name", "credit"]

    def get_category_name(self, obj):
        return obj.category.name if obj.category else "No Category"

    get_category_name.short_description = "Category"

    def get_state(self, obj):
        return obj.have_prerequisite_course

    get_state.short_description = "Prerequisite Course"


admin.site.register(Course, CourseAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    list_filter = ["name"]
    search_fields = ["name"]
    ordering = ["id"]


admin.site.register(Category, CategoryAdmin)
