from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .. import views

router = DefaultRouter()
router.register("users", views.AccountsViewSet, basename="users")

urlpatterns = [
    #   register / signup
    path("registration/", views.RegistrationApiView.as_view(), name="registration"),
    # login with token
    path("token/login/", views.CustomObtainAuthToken.as_view(), name="token-login"),
    # logout with token
    path("token/logout/", views.CustomDiscardAuthToken.as_view(), name="token-logout"),
    # jwt
    path("jwt/create/", views.CustomTokenObtainPairView.as_view(), name="jwt-create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt_refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt_verify"),
    # change password
    path(
        "change_password/",
        views.CustomChangePasswordApiView.as_view(),
        name="change-password",
    ),
    # reset password
    # reset password confirmation
    path(
        "password_reset/",
        views.CustomPasswordResetView.as_view(),
        name="custom_password_reset",
    ),
    path(
        "password_reset_done/",
        views.CustomPasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="custom_password_reset_done",
    ),
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="custom_password_reset_confirm",
    ),
    path(
        "password_reset_complete/",
        views.CustomPasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="custom_password_reset_complete",
    ),
]
urlpatterns += router.urls
