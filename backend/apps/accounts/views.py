from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.http import HttpResponse
from .models import User

def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'CLIENT'  # Force client role — no self-registration as admin
            user.is_active = True
            user.save()
            login(request, user)  # Log them in immediately after registration
            messages.success(request, "Registration successful! Welcome to Ticket2X.")
            return redirect('core:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

def debug_login(request):
    """Temporary debug view to force login as superuser"""
    try:
        user = User.objects.get(email='admin@ticket2x.com')
        login(request, user)
        return HttpResponse(
            f"<h2>Logged in successfully as {user.email}</h2>"
            f"<p>is_staff: {user.is_staff}</p>"
            f"<p>is_superuser: {user.is_superuser}</p>"
            f"<p>role: {user.role}</p>"
            f"<br><a href='/admin/'>Go to Admin Panel</a>"
        )
    except User.DoesNotExist:
        return HttpResponse("User 'admin@ticket2x.com' not found. Please create it first.")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")