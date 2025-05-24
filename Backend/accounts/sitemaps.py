from django.contrib.sitemaps import Sitemap
from .models import User, Profile


# Sitemap for the User model, helps search engines index user-related pages
class UserSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return User.objects.all()

    def lastmod(self, obj):
        return obj.created_date


# Sitemap for the Profile model, helps search engines index profile-related pages
class ProfileSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Profile.objects.all()

    def lastmod(self, obj):
        return obj.user.created_date
