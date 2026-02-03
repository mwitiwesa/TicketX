from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm


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
            messages.success(request, "Registration successful! Welcome to TicketX.")
            return redirect('core:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})