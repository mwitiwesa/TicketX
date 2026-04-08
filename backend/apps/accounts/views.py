from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Explicit backend to avoid "multiple backends" error
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Registration successful! Welcome to Ticket2X.")
            return redirect('core:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('accounts:login')

@login_required
def make_admin(request):
    """ Ultra simple promotion for testing """
    user = request.user
    
    # Force promotion
    user.role = 'ADMIN'
    user.is_staff = True
    user.is_superuser = True
    user.is_main_admin = True
    user.save()

    # Force a message
    messages.success(request, f"✅ PROMOTED {user.email} TO ADMIN - Please logout and login again")
    
    return redirect('core:home')