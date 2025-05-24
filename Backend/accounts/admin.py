from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile
from .forms import CustomUserCreationForm

# Register your models here.


class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for the User model.
    - Extends the default `UserAdmin` to use a custom user creation form.
    - Adds functionality to display, filter, search, and order user records in the admin panel.
    """

    add_form = CustomUserCreationForm

    model = User
    list_display = [
        "username",
        "email",
        "is_active",
        "is_superuser",
    ]
    list_filter = ["is_superuser", "username"]
    search_fields = ["username"]
    ordering = ["username", "email", "username"]
    fieldsets = (
        (
            "Authentication",
            {
                "fields": (
                    "email",
                    "username",
                    "password",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "is_verified",
                )
            },
        ),
        (
            "Group Permissions",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Date ", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "is_verified",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)


class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Profile model.
    - Customizes how Profile records are displayed, filtered, searched, and ordered in the admin panel.
    """

    model = Profile
    list_display = ["get_username", "get_fullname", "phone_number", "is_last_semester"]
    list_filter = ["user__username"]
    search_fields = ["user__username", "phone_number"]
    ordering = ["user__username", "last_name", "first_name"]

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = "Username"

    def get_fullname(self, obj):
        return (
            obj.first_name + " " + obj.last_name
            if (obj.first_name and obj.last_name)
            else "---"
        )

    get_fullname.short_description = "Fullname"


admin.site.register(Profile, ProfileAdmin)
