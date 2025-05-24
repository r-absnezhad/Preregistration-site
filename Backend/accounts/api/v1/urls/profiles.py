from django.urls import path
from .. import views


urlpatterns = [
    # check profile to have phone number
    path("check/", views.CheckProfileApiView.as_view(), name="check-profile"),
    # update phone number of profile
    path("update/", views.UpdateProfileApiView.as_view(), name="update-profile"),
    # information of a single profile.
    path("<str:pk>/", views.ProfileApiView.as_view(), name="profile-detail"),
    # a list of all profiles.
    path("", views.ProfileListApiView.as_view(), name="profile-list"),
]
