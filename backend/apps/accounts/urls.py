from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register
from .forms import LoginForm

app_name = "accounts"

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        authentication_form=LoginForm
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        next_page='accounts:login'
    ), name='logout'),

    path('register/', register, name='register'),
]