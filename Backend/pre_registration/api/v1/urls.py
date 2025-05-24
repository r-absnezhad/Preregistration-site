from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    RegistrationsViewSet,
    CourseViewSet,
    CategoryViewSet,
    ReportCourseApiView,
    CourseHistoryViewSet,
    PermittedCoursesApiView,
    ImportAPIView,
)

app_name = "api-v1"
# Create a router instance to automatically generate URL patterns for the API.
router = DefaultRouter()
router.register("registrations", RegistrationsViewSet, basename="registrations")
router.register("course", CourseViewSet, basename="course")
router.register("category", CategoryViewSet, basename="category")
router.register("course-history", CourseHistoryViewSet, basename="course-history")
urlpatterns = [
    path(
        "report_courses/<str:term_id>/",
        ReportCourseApiView.as_view(),
        name="course_report_api",
    ),
    path(
        "permitted-courses/",
        PermittedCoursesApiView.as_view(),
        name="permitted_courses",
    ),
    path("import/course-history/", ImportAPIView.as_view(), name="import_excel"),
]
urlpatterns += router.urls
