from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Contact


# Sitemap for StaticView, helps search engines index user-related pages
class StaticViewSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.4

    def items(self):
        return ["website:home", "website:about", "website:contact"]

    def location(self, item):
        return reverse(item)


# Sitemap for the Contact model, helps search engines index user-related pages
class ContactSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Contact.objects.all()

    def lastmod(self, obj):
        return obj.created_date
