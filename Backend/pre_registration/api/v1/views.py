import io
import pandas as pd
from django.http import HttpResponse
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from accounts.models import User, Profile
from ...models import Registrations, Course, Category, CourseHistory
from .utils import has_completed_prerequisite
from .permissions import IsStaffOrReadOnly, IsAuthenticatedOrAdmin, IsAdminOrReadOnly
from .serializers import (
    RegistrationsSerializer,
    CourseSerializer,
    CategorySerializer,
    CourseHistorySerializer,
    ImportSerializer,
)


class ImportAPIView(APIView):
    """
    API view for importing an Excel file containing user data for processing into the database.
    """

    serializer_class = ImportSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        try:
            data = request.FILES
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            excel_file = data.get("file")
            try:
                # Check if the file is an Excel file
                df = pd.read_excel(excel_file, sheet_name=0)
            except Exception as e:
                return Response(
                    {"details": f"Error reading Excel file: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            error_occurred = False
            error_details = []
            required_columns = [
                "Username",
                "Course_name",
                "Grade",
                "Status",
                "Last_average",
                "Is_last_semester",
            ]

            for index, row in df.iterrows():
                # Check if any required column is missing
                missing_columns = [
                    col for col in required_columns if pd.isnull(row[col])
                ]
                if missing_columns:
                    error_occurred = True
                    error_details.append(
                        f"Row {index + 1} is missing values for columns: {', '.join(missing_columns)}"
                    )
                    continue
                try:
                    # finding profile of users by username
                    profile = get_object_or_404(
                        Profile, user__username=str(row["Username"])
                    )
                    # finding corse id of courses by course name
                    course_name = row["Course_name"].strip()
                    course = get_object_or_404(Course, name__iexact=course_name)
                    # update profile with new fields
                    profile.last_average = float(row["Last_average"])
                    profile.is_last_semester = bool(row["Is_last_semester"])
                    profile.save()

                    # create CourseHistory
                    CourseHistory.objects.update_or_create(
                        profile=profile,
                        course=course,
                        defaults={"grade": row["Grade"], "status": row["Status"]},
                    )
                except Exception as e:
                    error_occurred = True
                    error_details.append(
                        f"Error processing row {index + 1}: {str(e)} (Row Data: {row.to_dict()})"
                    )

            if error_occurred:
                error_messages = [str(detail) for detail in error_details]
                return Response(
                    {
                        "details": f"Some rows could not be processed: {', '.join(error_messages)}",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"details": "فایل با موفقیت ایمپورت شد"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"details": f"File is not valid {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ReportCourseApiView(APIView):
    """
    This API view generates a report of courses and the total number of registrations for a specific term.
    Optionally, it can return the report in Excel format.
    """

    permission_classes = [IsAdminUser, IsAuthenticated]

    def post(self, request, term_id=None):
        """
        This function generates a report of courses in excel format. 
        """
        qs = Registrations.objects.filter(term=term_id)
        if not qs.exists():
            return Response(
                {"details": "No Registrations found for this term."},
                status=status.HTTP_404_NOT_FOUND,
            )

        counted_course = (
            qs.values("term", "courses_id__name")
            .annotate(total_requests=Count("id"))
            .order_by("courses_id__name")
        )
        renamed_data = [
            {
                "Term": item["term"],
                "Course Name": item["courses_id__name"],
                "Total Requests": item["total_requests"],
            }
            for item in counted_course
        ]
        df = pd.DataFrame(renamed_data)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Report")
        buffer.seek(0)

        response = HttpResponse(
            buffer.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="Report-courses.xlsx"'
        return response

    def get(self, request, term_id):
        terms = Registrations.objects.filter(term=term_id)
        if not terms.exists():
            return Response(
                {"details": "No Registrations found for this term."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if term_id:
            counted_course = (
                Registrations.objects.filter(term=term_id)
                .values("term", "courses_id__name")
                .annotate(total_requests=Count("id"))
                .order_by("courses_id__name")
            )

            # rename the columns
            renamed_data = [
                {
                    "Term": item["term"],
                    "Course Name": item["courses_id__name"],
                    "Total Requests": item["total_requests"],
                }
                for item in counted_course
            ]

            return Response(renamed_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"details": "You must select a term"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PermittedCoursesApiView(APIView):
    """
    This API view generates a list of permitted courses for a specific student and term.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, term_id=None):
        user = request.user
        profile = get_object_or_404(Profile, user=user)
        all_courses = Course.objects.all()

        completed_courses = CourseHistory.objects.filter(
            profile=profile, status="completed"
        ).values_list("course__id", flat=True)

        permitted_courses = all_courses.exclude(id__in=completed_courses)

        serializer = CourseSerializer(permitted_courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseHistoryViewSet(viewsets.ModelViewSet):
    """
    This viewset handles CourseHistory objects, allowing CRUD operations on course history records.
    """

    queryset = CourseHistory.objects.all()
    serializer_class = CourseHistorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "profile__user__username"]

    def create(self, request, *args, **kwargs):
        """
        Handles the creation or update of a course history record.
        Validates the data, checks the prerequisites, and determines the course status based on grade.
        """
        username = request.data.get("username")
        course_name = request.data.get("course")
        grade = request.data.get("grade")

        errors = {}

        if not username:
            errors["username"] = (
                "Username is required. Please provide a valid username."
            )

        if not course_name:
            errors["courses_id"] = (
                "Courses are required. Please provide at least one course name."
            )

        if grade is None:
            errors["grade"] = "Grade is required. Please provide a valid grade."

        if errors:
            return Response(
                {"detail": "Invalid input data.", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(User, username=username)

        course = get_object_or_404(Course, name=course_name)

        profile = get_object_or_404(Profile, user=user)
        grade = float(grade) if isinstance(grade, str) else grade

        if course.category == "Teaching-qualification":
            status_value = "completed" if grade >= 12 else "failed"
        else:
            status_value = "completed" if grade >= 10 else "failed"

        history = get_object_or_404(CourseHistory, profile=profile, course=course)

        if history:
            CourseHistory.objects.filter(profile=profile, course=course).update(
                grade=grade, status=status_value
            )
            message = f"History for {user.username} with {course.name} updated."
        else:
            history = CourseHistory.objects.create(
                profile=profile, course=course, grade=grade, status=status_value
            )
            message = f"History for {user.username} with {course.name} created."

        if not history.id:
            return Response(
                {"detail": "Failed to save the CourseHistory record."}, status=500
            )

        return Response(
            {"detail": message},
            status=status.HTTP_200_OK if history else status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path="completed-courses")
    def completed_courses(self, request):
        """
        Returns a list of completed courses for the authenticated user.
        """
        user = request.user
        profile = get_object_or_404(Profile, user=user)
        completed_courses = CourseHistory.objects.filter(
            profile=profile, status="completed"
        )
        serializer = self.get_serializer(completed_courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="failed-courses")
    def failed_courses(self, request):
        """
        Returns a list of failed courses for the authenticated user.
        """
        user = request.user
        profile = get_object_or_404(Profile, user=user)
        failed_courses = CourseHistory.objects.filter(profile=profile, status="failed")
        serializer = self.get_serializer(failed_courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RegistrationsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to handle Registrations model CRUD operations.
    This viewset provides endpoints for managing course registrations for users.
    It also validates prerequisites for courses and handles creating or updating registration records.
    """

    permission_classes = [IsAuthenticatedOrAdmin]
    serializer_class = RegistrationsSerializer
    queryset = Registrations.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["term", "courses_id"]
    search_fields = ["term"]
    ordering_fields = ["created_date", "term"]

    def perform_create(self, serializer):
        """
        Override perform_create to automatically associate the logged-in user with the registration.
        """
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer.save(user_id=profile)

    def create(self, request, *args, **kwargs):
        """
        Handle creating or updating a registration for a user in a given term.
        Validates the user, courses, and prerequisites before allowing the registration.
        """
        term = request.data.get("term")
        if hasattr(request.data, "getlist"):  # if it is a QueryDict
            courses_id = request.data.getlist("courses_id", [])
        else:  # if it is a dict
            courses_id = request.data.get("courses_id", [])
            if not isinstance(courses_id, list):
                courses_id = [courses_id]
        errors = {}


        if not courses_id:
            errors["courses"] = "هیچ درسی انتخاب نشده است. لطفاً حداقل یک درس را انتخاب کنید."
        if errors:
            return Response(
                {
                    "detail": "اطلاعات ورودی نامعتبر است. لطفاً مشکلات زیر را برطرف کنید.",
                    "errors": errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = get_object_or_404(Profile, user=request.user)
        courses = Course.objects.filter(id__in=courses_id)
        if not courses:
            return Response({"detail": "برخی از دروس یافت نشدند."}, status=404)

        for course in courses:
            if not has_completed_prerequisite(profile, course):
                return Response(
                    {
                        "detail": f"پیش‌نیاز درس «{course.name}» گذرانده نشده است."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            

        # Check if a registration already exists for this user and term
        existing_registration = Registrations.objects.filter(user_id=profile, term=term).first()
        if existing_registration:
            return Response(
            {"detail": "شما قبلاً در این ترم پیش ثبت‌نام کرده‌اید."},
            status=status.HTTP_400_BAD_REQUEST,
        )
        # Create a new registration
        registration = Registrations.objects.create(
            user_id=profile, term=term
        )
        registration.courses_id.add(*courses)
        registration.save()

        serializer = RegistrationsSerializer(registration)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="user-registrations/(?P<username_id>[\\w]+)",
    )
    def get_user_registrations(self, request, username_id=None):
        get_object_or_404(User, username=username_id)

        pre_registrations = Registrations.objects.filter(
            user_id__user__username=username_id
        )
        if pre_registrations:
            serializer = RegistrationsSerializer(pre_registrations, many=True)
            return Response(serializer.data)
        else:
            return Response(
                {
                    "detail": "هیچ ثبت‌نامی برای این کاربر یافت نشد.",
                    "information": pre_registrations,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet to handle Course model CRUD operations.
    This viewset provides endpoints for managing courses and their details.
    """

    permission_classes = [IsAdminOrReadOnly]
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["category"]
    search_fields = ["name", "credit"]
    ordering_fields = ["name"]


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet to handle Category model CRUD operations.
    This viewset provides endpoints for managing course categories.
    """

    permission_classes = [IsStaffOrReadOnly]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["name"]
    search_fields = ["name"]
    ordering_fields = ["name"]

    def retrieve(self, request, pk=None):
        if pk:
            category = get_object_or_404(Category, id=pk)
            serializer = self.serializer_class(category)
            courses = Course.objects.filter(category=category)
            courses_serializer = CourseSerializer(courses, many=True)
            data = {
                "category": serializer.data,
                "courses": courses_serializer.data,
            }
            return Response(data, status=status.HTTP_200_OK)
