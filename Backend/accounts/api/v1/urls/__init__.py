from django.urls import path, include

urlpatterns = [
    path("", include("accounts.api.v1.urls.account")),
    path("profile/", include("accounts.api.v1.urls.profiles")),
]
