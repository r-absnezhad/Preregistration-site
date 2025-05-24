from django import forms
from simplemathcaptcha.fields import MathCaptchaField
from .models import Registrations, Course


class PreRegistrationForm(forms.ModelForm):
    """
    Form for registering a user for courses.
    Includes a captcha field for verification and a multiple-choice field for course selection.
    """

    captcha = MathCaptchaField()
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = Registrations
        fields = "__all__"

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.cleaned_data["courses"].set(instance.courses.all())
        return instance
