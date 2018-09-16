from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    """Enhances Django signup form"""
    email = forms.EmailField(max_length=200, required=False)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')