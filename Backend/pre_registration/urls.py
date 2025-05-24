from django.urls import path, include

app_name = "pre_registration"
urlpatterns = [
    path("api/v1/", include("pre_registration.api.v1.urls", namespace="api-v1")),
]
