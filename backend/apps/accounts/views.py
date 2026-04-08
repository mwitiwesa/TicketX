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
    """ Temporary function to promote the currently logged-in user to admin """
    user = request.user
    
    print(f"DEBUG: Promoting user {user.email} - Current role: {user.role}")  # This will show in Render Logs

    user.role = 'ADMIN'
    user.is_staff = True
    user.is_superuser = True
    user.is_main_admin = True
    user.save()

    messages.success(request, f"✅ Successfully promoted {user.email} to Admin!")
    return redirect('core:home')