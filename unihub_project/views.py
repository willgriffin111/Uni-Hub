from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from api.posts.models import Post, Comment
from api.community.models import Community
from django.utils import timezone
from django.db.models import Count


@login_required
def home_page(request):
    """Render the post display page with correct like count and user like status, 
    and show top 3 communities with the most members."""
    
    posts = Post.objects.all().order_by('-created_at')  # Order by newest first
    current_time = timezone.now()
    
    # For each post, get like count, check if the user liked it, and get comment count
    for post in posts:
        post.likes_count = post.likes.count()  # Get total like count
        post.liked = post.likes.filter(user=request.user).exists()  # Check if the user has liked this post
        post.comments_count = post.comments.count()
        
        # Check if the post was created within 30 minutes (for edit permission)
        post.can_edit = (current_time - post.created_at).total_seconds() <= 30 * 60
    
    # Retrieve the top 3 communities with the most members
    top_communities = Community.objects.annotate(num_members=Count('members')).order_by('-num_members')[:3]
    
    return render(request, 'pages/home_page.html', {
        'posts': posts, 
        'user': request.user,
        'top_communities': top_communities  
    })

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
def profile_view(request):
    """Render the profile page (requires login)."""
    posts = Post.objects.filter(user_id=request.user).order_by('-created_at')  # '-' makes it descending (newest first)
    return render(request, "pages/profile.html", {"user": request.user, "posts": posts})


def edit_post(request, post_id):
    # Get the post ID from the URL
    post = get_object_or_404(Post, id=post_id)  # Ensure the post exists
    return render(request, 'pages/post_edit.html', {'post': post})

def password_reset_view(request):
    return render(request, "pages/password_reset.html")

def password_reset_confirm_view(request):
    return render(request, "pages/password_reset_confirm.html")

@login_required
def edit_comment_view(request, comment_id):
    """Render the edit comment page."""
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)  # Ensure only the owner can edit
    return render(request, 'pages/edit_comment.html', {'comment': comment})

def search_view(request):
    return render(request, 'pages/search_page.html')


#community views
@login_required
def community_view(request, community_name):
    community = get_object_or_404(Community, name=community_name)
    posts = Post.objects.filter(community=community.id).order_by('-created_at')  # Order by newest first
    current_time = timezone.now()
    for post in posts:
        post.likes_count = post.likes.count()  # Get total like count
        post.liked = post.likes.filter(user=request.user).exists()  # Check if the user has liked this post
        post.comments_count = post.comments.count()
        
        
        # Check if the post was created within 30 minutes (for edit permission)
        post.can_edit = (current_time - post.created_at).total_seconds() <= 30 * 60

    return render(request, "pages/community.html", {'community': community, 'posts': posts, "user": request.user})

@login_required
def community_edit_view(request, community_name):
    community = get_object_or_404(Community, name=community_name)
    return render(request, "pages/community_edit.html", {'community': community, "user": request.user})
# THESE ARE OLD VIEWS:

@login_required
def post_view(request):
    """Render the profile page (requires login)."""
    return render(request, "pages/posts.html", {"user": request.user})

@login_required
def post_list(request):
    """Render the post display page with correct like count and user like status."""
    
    posts = Post.objects.all().order_by('-created_at')  # Order by newest first
    current_time = timezone.now()
    for post in posts:
        post.likes_count = post.likes.count()  # Get total like count
        post.liked = post.likes.filter(user=request.user).exists()  # Check if the user has liked this post
        post.comments_count = post.comments.count()
        
        
        # Check if the post was created within 30 minutes (for edit permission)
        post.can_edit = (current_time - post.created_at).total_seconds() <= 30 * 60

    return render(request, 'pages/post_display.html', {'posts': posts, 'current_time': current_time})

@login_required
def dashboard_view(request):
    """Render the dashboard page (requires login)."""
    return render(request, "pages/dashboard.html", {"user": request.user})
