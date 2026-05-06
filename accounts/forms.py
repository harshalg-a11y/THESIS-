from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ["username", "email", "role", "password1", "password2"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "bio", "skills", "portfolio_url", "avatar_url"]
