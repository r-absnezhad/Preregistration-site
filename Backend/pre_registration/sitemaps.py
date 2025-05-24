from django.contrib.sitemaps import Sitemap
from .models import Registrations, Course, Category


# Sitemap for the Registrations model, helps search engines index user-related pages
class RegistrationsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Registrations.objects.all()

    def lastmod(self, obj):
        return obj.created_date


# Sitemap for the Course model, helps search engines index user-related pages


class CourseSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.5

    def items(self):
        return Course.objects.all()

    def lastmod(self, obj):
        return obj.created_date


# Sitemap for the Category model, helps search engines index user-related pages


class CategorySitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.5

    def items(self):
        return Category.objects.all()
