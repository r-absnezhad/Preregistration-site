from django.contrib import admin
from .models import Contact


# Register your models here.
class ContactAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Contact model.
    - Customizes how Contact records are displayed, filtered, searched, and ordered in the admin panel.
    """

    date_hierarchy = "created_date"
    ordering = ["created_date"]
    list_display = ("id", "email", "subject", "created_date")
    list_filter = ("email", "created_date")


admin.site.register(Contact, ContactAdmin)
