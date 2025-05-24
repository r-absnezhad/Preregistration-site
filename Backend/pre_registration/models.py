from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

# Create your models here.
# getting user model object
User = get_user_model()


class Registrations(models.Model):
    """
    Stores pre-registration details for students.
    Includes user profile, selected courses, and the term for registration.
    Automatically calculates max_units based on the student's GPA.
    """

    term = models.CharField(max_length=255)
    user_id = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE)
    courses_id = models.ManyToManyField("Course")
    # max_units = models.IntegerField(default=20)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def get_absolute_url(self):
        return reverse(
            "pre_registration:api-v1:registrations-detail", kwargs={"pk": self.pk}
        )

    def __str__(self):
        return f"{self.term} . {self.user_id.user.username}"


class Course(models.Model):
    """
    Stores information about academic courses.
    Includes optional prerequisites and belongs to a specific category.
    """

    name = models.CharField(max_length=255)
    credit = models.IntegerField(default=0)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)
    have_prerequisite_course = models.BooleanField(default=False)
    prerequisite_course = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="dependent_courses"
    )
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def get_absolute_url(self):
        return reverse("pre_registration:api-v1:course-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Represents a category for grouping courses, e.g., "اصلی" or "تخصصی".
    """

    name = models.CharField(max_length=255)

    def get_absolute_url(self):
        return reverse(
            "pre_registration:api-v1:category-detail", kwargs={"pk": self.pk}
        )

    def __str__(self):
        return self.name


class CourseHistory(models.Model):
    """
    Tracks the history of courses taken by a student.
    Includes details about the grade, status, and associated profile.
    """

    profile = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="course_histories"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, null=False, related_name="course_histories"
    )
    grade = models.DecimalField(
        max_digits=4, decimal_places=2, null=False, blank=True, default=0.00
    )
    status = models.CharField(
        max_length=30,
        choices=[
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = (
            "profile",
            "course",
        )

    # def save(self, *args, **kwargs):
    #     if self.grade is not None:
    #         if self.course.category == "صلاحیت معلمی":
    #             self.status = "completed" if self.grade >= 12 else "failed"
    #         else:
    #             self.status = "completed" if self.grade >= 10 else "failed"
    #     else:
    #         self.status = "in_progress"
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profile.user.username} - {self.course.name} - {self.status}"
