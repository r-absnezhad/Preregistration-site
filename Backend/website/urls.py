from django.urls import path, include
from .views import IndexAPIView

app_name = "website"
urlpatterns = [
    path("api/v1/", include("website.api.v1.urls", namespace="api-v1")),
    path("", IndexAPIView.as_view(), name="index"),
]
