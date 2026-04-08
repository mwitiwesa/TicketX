from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'placeholder': 'Enter your email address',
            'class': 'form-control'   # optional for styling
        })
    )

    def clean_username(self):
        #  return the email as username for the backend
        return self.cleaned_data.get('username')