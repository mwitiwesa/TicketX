from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import User 

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

def promote_admin(request):
    """ One-time promotion endpoint """
    try:
        user = User.objects.get(email='admin1@ticket2x.com')   # Change this email if you used a different one
        user.role = 'ADMIN'
        user.is_staff = True
        user.is_superuser = True
        user.is_main_admin = True
        user.save()
        return HttpResponse(f"<h2 style='color:green;'>✅ Successfully promoted {user.email} to Admin!</h2><p>You can now logout and login again as admin.</p>")
    except User.DoesNotExist:
        return HttpResponse(f"<h2 style='color:red;'>User with email adminfinal@ticket2x.com not found.</h2><p>Please register this email first.</p>")