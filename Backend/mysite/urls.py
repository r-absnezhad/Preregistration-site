from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from website.sitemaps import StaticViewSitemap, ContactSitemap
from pre_registration.sitemaps import (
    RegistrationsSitemap,
    CourseSitemap,
    CategorySitemap,
)
from accounts.sitemaps import UserSitemap, ProfileSitemap

schema_view = get_schema_view(
    openapi.Info(
        title="Project API",
        default_version="v1",
        description="Test api",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="	reihaneabbasnezhadsarab@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

sitemaps = {
    "static": StaticViewSitemap,
    "contact": ContactSitemap,
    "registrations": RegistrationsSitemap,
    "course": CourseSitemap,
    "category": CategorySitemap,
    "user": UserSitemap,
    "profile": ProfileSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("pre_registration/", include("pre_registration.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("robots.txt", include("robots.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path(
        "swagger/api.json",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("captcha/", include("captcha.urls")),
    path("", include("website.urls")),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
