from rest_framework.routers import DefaultRouter
from .views import ContactViewSet

app_name = "api-v1"
# Create a router instance to automatically generate URL patterns for the API.
router = DefaultRouter()
router.register("contact", ContactViewSet, basename="contact")
urlpatterns = router.urls
