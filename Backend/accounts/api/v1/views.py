from django.http import Http404
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, generics
from rest_framework.filters import SearchFilter
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from mail_templated import EmailMessage
from .permissions import IsAuthenticatedOrAdmin, IsProfileOwnerOrAdmin
from .utils import EmailThread
from ...models import Profile
from .serializers import (
    UserSerializer,
    ProfileSerializer,
    RegistrationSerializer,
    CustomAuthTokenSerializer,
    CustomTokenObtainPairSerializer,
    CustomChangePasswordSerializer,
    UpdateProfileSerializer,
)

User = get_user_model()


class CustomPasswordResetView(PasswordResetView):
    """
    A custom password reset view that extends Django's built-in PasswordResetView.
    """

    success_url = reverse_lazy("accounts:custom_password_reset_done")

    extra_email_context = {
        "domain": settings.DEFAULT_DOMAIN,
        "protocol": settings.DEFAULT_PROTOCOL,
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(kwargs)
        return context


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    A custom password reset confirm view that extends Django's built-in PasswordResetView.
    """

    success_url = reverse_lazy("accounts:custom_password_reset_complete")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    title = _("Password reset sent, please check your email")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
    A custom password reset complete view that extends Django's built-in PasswordResetView.
    """

    title = _("Password reset completed successfully")



class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for obtaining JWT access and refresh tokens.
    """

    serializer_class = CustomTokenObtainPairSerializer


class CustomChangePasswordApiView(generics.GenericAPIView):
    """
    API view for handling user password changes.
    This view allows authenticated users to change their password by providing
    their current password and a new password.
    """

    serializer_class = CustomChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    model = User

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        """
        Handle PUT requests to change the user's password.
        - Validates the old password.
        - Ensures the new password is different from the old password.
        - Saves the new password and updates the user's state.
        """
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": "Wrong password"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if serializer.data.get("old_password") == serializer.data.get(
                "new_password"
            ):
                return Response(
                    {"new_password": "passwords must be different"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(
                {"details": "Password changed successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrationApiView(generics.GenericAPIView):
    """
    API view for user registration.
    Handles user sign-up, generates an activation token, and sends an activation email.
    """

    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for user registration.
        - Validates the registration data using the serializer.
        - Creates a new user if the data is valid.
        - Generates an activation token for the user.
        - Sends an activation email to the user with the token.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data["email"]
            data = {
                "email": email,
            }

            user_obj = get_object_or_404(User, email=email)
            token = self.get_tokens_for_user(user_obj)
            email_obj = EmailMessage(
                "email/activation_email.tpl",
                {"token": token},
                "reihaneabbasnezhadsarab@gmail.com",
                to=[email],
            )
            EmailThread(email_obj).start()
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class CustomObtainAuthToken(ObtainAuthToken):
    """
    Custom view for user authentication using token-based authentication.
    Extends the default `ObtainAuthToken` to return additional user details along with the token.
    """

    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for user authentication.
        - Validates the user credentials using the custom serializer.
        - If valid, generates or retrieves an authentication token for the user.
        - Returns the token along with additional user details (user ID, email, username).
        """
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        token, created = Token.objects.get_or_create(user=user)
        # send access_token
        refresh = RefreshToken.for_user(user)
        is_admin = user.is_staff or user.is_superuser

        return Response(
            {
                "token": str(refresh.access_token),
                "user_id": user.pk,
                "email": user.email,
                "username": user.username,
                "is_admin": is_admin,
            }
        )


class CustomDiscardAuthToken(APIView):
    """
    API view for discarding (logging out) the authentication token.
    Allows authenticated users to manually invalidate their token by deleting it.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user accounts.
    - Provides CRUD operations for user accounts.
    - Accessible only to authenticated users with admin privileges.
    - Supports filtering, searching, and ordering of user data.
    """

    permission_classes = [IsAuthenticatedOrAdmin]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = {"username": ["exact", "in"], "email": ["exact", "in"]}
    search_fields = ["username", "email", "is_active", "is_verified"]
    ordering_fields = ["username", "email"]

    def get_object(self):
        """
        Retrieve a single user object based on the 'username' lookup field.
        - The `pk` in the URL is treated as the username.
        - Raises a 404 error if no user is found with the specified username.
        """
        lookup_field = "username"
        lookup_value = self.kwargs.get("pk")
        try:
            return self.queryset.get(**{lookup_field: lookup_value})
        except self.queryset.model.DoesNotExist:
            raise Http404(f"No user found with {lookup_field}={lookup_value}")


class ProfileListApiView(generics.ListAPIView):
    """
    API view for listing all profiles.
    - Provides a read-only endpoint for listing all profile records in the database.
    - Accessible only to authenticated admin users.
    - Supports filtering, searching, and ordering.
    """

    permission_classes = [IsAdminUser, IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["phone_number", "last_name", "first_name"]
    search_fields = ["is_last_semester", "phone_number", "first_name", "last_name"]
    ordering_fields = ["last_name", "first_name"]


class ProfileApiView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating a specific profile.
    - Allows admin users to retrieve or update the profile details of a specific user.
    - Supports filtering, searching, and ordering.
    - Retrieves the profile based on the user's username (provided in the URL).
    """

    permission_classes = [IsProfileOwnerOrAdmin]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["phone_number", "last_name", "first_name", "is_last_semester"]
    search_fields = ["phone_number", "first_name", "last_name"]
    ordering_fields = ["last_name", "first_name"]


class CheckProfileApiView(APIView):
    """
    View to check whether the authenticated user has all information in their profile.

    This view allows users to verify if their profile contains all needed information. It is a read-only operation
    and requires the user to be authenticated.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_object_or_404(Profile, user__username=request.user.username)
        data = {
            "has_all_information": bool(
                profile.first_name and profile.last_name and profile.phone_number
            ),
        }
        return Response(data)


class UpdateProfileApiView(APIView):
    """
    View to update the phone number of the authenticated user's profile.

    This view allows authenticated users to update their phone number. The phone number is required
    to be provided in the request. If the phone number is successfully updated, a success message is returned.
    If no phone number is provided, an error message is returned.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UpdateProfileSerializer

    @swagger_auto_schema(
        request_body=UpdateProfileSerializer,
        responses={
            200: openapi.Response("Profile updated successfully!"),
            400: openapi.Response("Validation Error!"),
        },
    )
    def patch(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.serializer_class(profile, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile updated successfully!"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    