from django import forms
from .models import User, Profile


# Custom form to handle user creation with password confirmation and validation
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="confirm password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(attrs={"autocomplete": "off"}),
            "password1": forms.PasswordInput(attrs={"autocomplete": "new-password"}),
            "password2": forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("two passwords must match")
        if len(password1) != 10:
            raise forms.ValidationError("password must be at least 10 characters")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# Form to handle profile creation or updating
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "phone_number", "is_last_semester"]
