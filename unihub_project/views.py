from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def login_view(request):
    """Render the login page."""
    return render(request, "pages/login.html")

def register_view(request):
    """Render the register page."""
    return render(request, "pages/register.html")

@login_required
def Verify_view(request):
    """Render the one time password page."""
    return render(request, "pages/OTP.html")

@login_required
def dashboard_view(request):
    """Render the dashboard page (requires login)."""
    return render(request, "pages/dashboard.html", {"user": request.user})
