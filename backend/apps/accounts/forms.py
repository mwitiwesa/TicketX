from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )

    class Meta:
        model = User
        fields = ('email', 'password')