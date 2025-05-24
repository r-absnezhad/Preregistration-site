from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)


# Create your models here.
class UserManager(BaseUserManager):
    """
    Custom user model manager where username is the unique identifiers
    for authentication.
    """

    def create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username and email and password and extra data.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        if not username:
            raise ValueError(_("The Username must be set"))
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given username and email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Create Custom User Model which username is the unique identifiers for Authentication.
    """

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    objects = UserManager()

    def get_absolute_url(self):
        return reverse("accounts:users-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.username
