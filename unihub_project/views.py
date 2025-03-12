from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from api.posts.models import Post
from django.utils import timezone

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
    posts = Post.objects.filter(user_id=request.user).order_by('-created_at')  # '-' makes it descending (newest first)
    return render(request, "pages/profile.html", {"user": request.user, "posts": posts})

@login_required
def post_view(request):
    """Render the profile page (requires login)."""
    return render(request, "pages/posts.html", {"user": request.user})

@login_required

def post_list(request):
    # Order the posts by creation time (newest first)
    posts = Post.objects.all().order_by('-created_at')  # '-' makes it descending (newest first)
    current_time = timezone.now()
    for post in posts:
        # Check if the post was created within 30 minutes
        if (current_time - post.created_at).total_seconds() <= 30 * 60:
            post.can_edit = True
        else:
            post.can_edit = False
    return render(request, 'pages/post_display.html', {'posts': posts, 'current_time': current_time})

def edit_post(request, post_id):
    # Get the post ID from the URL
    post = get_object_or_404(Post, id=post_id)  # Ensure the post exists
    return render(request, 'pages/post_edit.html', {'post': post})

def password_reset_view(request):
    return render(request, "pages/password_reset.html")

def password_reset_confirm_view(request):
    return render(request, "pages/password_reset_confirm.html")


