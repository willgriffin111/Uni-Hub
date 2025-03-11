from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from api.posts.models import Post

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

@login_required
def profile_view(request):
    """Render the profile page (requires login)."""
    return render(request, "pages/profile.html", {"user": request.user})

@login_required
def post_view(request):
    """Render the profile page (requires login)."""
    return render(request, "pages/posts.html", {"user": request.user})

@login_required

def post_list(request):
    # Order the posts by creation time (newest first)
    posts = Post.objects.all().order_by('-created_at')  # '-' makes it descending (newest first)

    return render(request, 'pages/post_display.html', {'posts': posts})


def password_reset_view(request):
    return render(request, "pages/password_reset.html")

def password_reset_confirm_view(request):
    return render(request, "pages/password_reset_confirm.html")


