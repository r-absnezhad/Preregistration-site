from django.db import models
from django.urls import reverse


# Create your models here.
class Contact(models.Model):
    """
    Represents a contact message submitted by a user.
    - Stores the sender's name, email, subject, and message content.
    """

    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created_date",)

    def get_absolute_url(self):
        return reverse("website:api-v1:contact-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name
