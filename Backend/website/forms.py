from django import forms
from simplemathcaptcha.fields import MathCaptchaField
from .models import Contact


class ContactForm(forms.ModelForm):
    """
    Form for users to submit contact messages.
    - Based on the `Contact` model.
    - Includes a math captcha field for spam prevention.
    """

    captcha = MathCaptchaField()

    class Meta:
        model = Contact
        fields = "__all__"
