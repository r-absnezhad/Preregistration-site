from django.db import models
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save
from .users import User


class Profile(models.Model):
    """
    Represents the user's profile, extending the default User model.
    Includes personal details like image, name, GPA, and phone number.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    last_average = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    max_units = models.IntegerField(default=20)
    phone_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
    is_last_semester = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def get_absolute_url(self):
        return reverse("accounts:profile-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        last_gpa = self.last_average if self.last_average is not None else 0
        if last_gpa < 12:
            self.max_units = 20
        elif last_gpa >= 17:
            self.max_units = 29
        else:
            self.max_units = 24

        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
