from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from api.posts.models import Post, Comment
from django.utils import timezone
from api.community.models import Community, CommunityEvent, CommunityRole
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .decorators import verification_required

User = get_user_model()


@login_required
@verification_required
def home_page(request):
    """Render the home page with posts, top communities, 
    and upcoming events (posts are cached for 10 minutes per user)."""
    
    # Define a cache key unique for the current user.
    cache_key = f"posts"
    current_time = timezone.now()
    
    # Attempt to retrieve the posts list from cache.
    posts = cache.get(cache_key)
    if posts is None:
        print(f"\n Cache miss for key: {cache_key}. Querying database for posts.")
        # Cache miss: Query the database and process posts.
        posts = list(Post.objects.all().order_by('-created_at'))
        for post in posts:
            post.likes_count = post.likes.count()
            post.liked = post.likes.filter(user=request.user).exists()
            post.comments_count = post.comments.count()
            post.can_edit = (current_time - post.created_at).total_seconds() <= 30 * 60
        # Cache the posts list for 600 seconds (10 minutes)
        cache.set(cache_key, posts, timeout=600)
        print(f"Set cache key: {cache_key} with {len(posts)} posts.")
    else:
        print(f"\n Cache hit for key: {cache_key}. Updating dynamic fields for {len(posts)} posts.")
        # Cache hit: Update dynamic fields so that like and comment counts are current.
        for post in posts:
            post.likes_count = post.likes.count()
            post.liked = post.likes.filter(user=request.user).exists()
            post.comments_count = post.comments.count()
            post.can_edit = (current_time - post.created_at).total_seconds() <= 30 * 60

    # Retrieve top 3 communities with most members.
    top_communities = Community.objects.annotate(num_members=Count('members')).order_by('-num_members')[:4]
    
    now_date = current_time.date()
    upcoming_events = CommunityEvent.objects.filter(event_date__gte=now_date).annotate(
        attendance_count=Count('attendances')
    ).order_by('-attendance_count')[:4]
    
    current_user = request.user
    # Retrieve friend suggestions, excluding the current user current friends and root.
    suggestions = User.objects.exclude(id=current_user.id)\
                    .exclude(id__in=current_user.friends.values_list('id', flat=True))\
                    .exclude(username="root")[:4]
                    
    return render(request, 'pages/home_page.html', {
        'posts': posts,
        'user': request.user,
        'top_communities': top_communities,
        'events': upcoming_events,
        'suggestions': suggestions
    })

def login_view(request):
    """Render the login page."""
    return render(request, "pages/login.html")

def register_view(request):
    """Render the register page."""
    return render(request, "pages/register.html")

def Verify_view(request):
    if not request.session.get('otp_code'):
        if request.user.is_authenticated:
            return redirect('/profile/')
        else:
            return redirect('/login/')
    return render(request, 'pages/OTP.html')


@verification_required
@login_required
def profile_view(request):
    cache_key = f"posts"
    current_time = timezone.now()
    # Retrieve the posts from the home page cache.
    posts_all = cache.get(cache_key)
    if posts_all is None:
        print(f"\n Cache miss for key: {cache_key}. Querying database for posts.")
        posts_all = list(Post.objects.all().order_by('-created_at'))
        for post in posts_all:
            post.likes_count = post.likes.count()
            post.liked = post.likes.filter(user=request.user).exists()
            post.comments_count = post.comments.count()
            post.can_edit = (current_time - post.created_at).total_seconds() <= 30 * 60
        print(f"Set cache key: {cache_key} with {len(posts_all)} posts.")
        cache.set(cache_key, posts_all, timeout=600)
    else:
        print(f"\n Cache hit for key: {cache_key}. Updating dynamic fields for {len(posts_all)} posts.")
        for post in posts_all:
            post.likes_count = post.likes.count()
            post.liked = post.likes.filter(user=request.user).exists()
            post.comments_count = post.comments.count()
            post.can_edit = (current_time - post.created_at).total_seconds() <= 30 * 60

    # Filter for posts belonging to the logged-in user.
    user_posts = []
    for post in posts_all:
        if post.user == request.user:
            post.likes_count = post.likes.count()
            post.liked = post.likes.filter(user=request.user).exists()
            post.comments_count = post.comments.count()
            post.can_edit = (current_time - post.created_at).total_seconds() <= 30 * 60
            user_posts.append(post)
    
    return render(request, "pages/profile.html", {"user": request.user, "posts": user_posts})

@login_required
@verification_required
def profile_edit_view(request):
    """Render the profile edit page."""
    return render(request, "pages/profile_edit.html")

@login_required
@verification_required
def edit_post(request, post_id):
    # Get the post ID from the URL
    post = get_object_or_404(Post, id=post_id)  # Ensure the post exists
    return render(request, 'pages/post_edit.html', {'post': post})


def password_reset_view(request):
    return render(request, "pages/password_reset.html")

def password_reset_confirm_view(request):
    return render(request, "pages/password_reset_confirm.html")

@login_required
@verification_required
def edit_comment_view(request, comment_id):
    """Render the edit comment page."""
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)  # Ensure only the owner can edit
    return render(request, 'pages/edit_comment.html', {'comment': comment})

@login_required
@verification_required
def search_view(request):
    return render(request, 'pages/search.html')


#community views

ROLE_HIERARCHY = {
        "member": 1,
        "event_leader": 2,
        "community_leader": 3,
        "admin": 4,
    }

@verification_required
@login_required
def community_view(request, community_name):
    community = get_object_or_404(Community, name=community_name)
    if community.is_user_blocked(request.user):
        return redirect('index_page')
    cache_key = f"posts"
    current_time = timezone.now()
    
    posts_all = cache.get(cache_key)
    if posts_all is None:
        print(f"\n Cache miss for key: {cache_key}. Querying database for posts.")
        posts_all = list(Post.objects.all().order_by('-created_at'))
        for post in posts_all:
            post.likes_count = post.likes.count()
            post.liked = post.likes.filter(user=request.user).exists()
            post.comments_count = post.comments.count()
            post.can_edit = (current_time - post.created_at).total_seconds() <= 30 * 60
        print(f"Set cache key: {cache_key} with {len(posts_all)} posts.")
        cache.set(cache_key, posts_all, timeout=600)
    else:
        print(f"\n Cache hit for key: {cache_key}. Updating dynamic fields for {len(posts_all)} posts.")
        for post in posts_all:
            post.likes_count = post.likes.count()
            post.liked = post.likes.filter(user=request.user).exists()
            post.comments_count = post.comments.count()
            post.can_edit = (current_time - post.created_at).total_seconds() <= 30 * 60

    # Filter posts to only those in the requested community.
    community_posts = []
    for post in posts_all:
        if post.community == community:
            # Update dynamic fields for each post in the community.
            post.likes_count = post.likes.count()
            post.liked = post.likes.filter(user=request.user).exists()
            post.comments_count = post.comments.count()
            post.can_edit = (current_time - post.created_at).total_seconds() <= 30 * 60
            community_posts.append(post)

    # Load additional community data (members, etc.) as needed.
    members = community.members.all()
    members_count = members.count()
    is_member = request.user in members
    ROLE_HIERARCHY = {"member": 1, "event_leader": 2, "community_leader": 3, "admin": 4}
    user_role_level = 0
    if is_member:
        user_role = CommunityRole.objects.filter(community=community, user=request.user).first()
        user_role_level = ROLE_HIERARCHY.get(user_role.role, 0)
        
    for member in members:
        role = CommunityRole.objects.filter(community=community, user=member).first()
        member.role = role
        member.role_level = ROLE_HIERARCHY.get(role.role, 0) if role else 0
        
    members = sorted(members, key=lambda m: m.role_level, reverse=True)
        
    is_creator = community.created_by == request.user
    

    return render(request, 'pages/community_view.html', {
        "community": community,
        "posts": community_posts,
        "user": request.user,
        "members": members,
        "members_count": members_count,
        "user_role_level": user_role_level,
        "is_member": is_member,
        "is_creator": is_creator,
    })

@verification_required
@login_required
def community_list_view(request):
    """Show a list of communities."""
    communities = Community.objects.all()  # Fetch all communities
    return render(request, "pages/community_create.html", {"communities": communities})

@verification_required
@login_required
def community_create_page(request):
    """Render the form to create a new community."""
    return render(request, "pages/community_create.html")

    return render(request, "pages/community.html", {'community': community, 'posts': posts, "user": request.user})

@verification_required
@login_required
def community_edit_view(request, community_name):
    community = get_object_or_404(Community, name=community_name)
    # Get the members of the community
    members = community.members.all()
    
    # Check if the current user is a member of the community and their role
    is_member = request.user in members
    if is_member:
        user_role = CommunityRole.objects.filter(community=community, user=request.user).first() 
        if user_role:
            user_role_level = ROLE_HIERARCHY.get(user_role.role, 0)
            if user_role_level >= 3 :
                return render(request, "pages/community_edit.html", {'community': community, "user": request.user})
    
    return redirect('community_page', community_name=community_name)

@verification_required
@login_required
def community_manage_view(request, community_name):
    community = get_object_or_404(Community, name=community_name)
    # Get the members of the community
    members = community.members.all()
    
    # Check if the current user is a member of the community and their role
    is_member = request.user in members
    if is_member:
        
        user_role = CommunityRole.objects.filter(community=community, user=request.user).first()
        user_role_level = ROLE_HIERARCHY.get(user_role.role, 0)
        if user_role_level >= 3:
            # return redirect('community_page', community_name=community_name)
        
            for member in members:
                role = CommunityRole.objects.filter(community=community, user=member).first()
                member.role = role
                member.role_level = ROLE_HIERARCHY.get(role.role, 0) if role else 0
                member.is_blocked = community.is_user_blocked(member)
                
            members = sorted(members, key=lambda m: m.role_level, reverse=True)
                
            is_creator = community.created_by == request.user
            
            return render(request, "pages/community_manage.html", {'community': community, "members": members, "user": request.user, "user_role_level": user_role_level, "is_creator": is_creator})
    return redirect('community_page', community_name=community_name)
        

@login_required
@verification_required
def event_edit_view(request, event_id):
    event = get_object_or_404(CommunityEvent, id=event_id)
    community = event.community
    user_role = CommunityRole.objects.filter(community=community, user=request.user).first()
    user_role_level = ROLE_HIERARCHY.get(user_role.role, 0)
    
    if user_role and user_role_level >= 2:
        return render(request, 'pages/event_edit.html', {'event': event})
    
    return redirect('community_page', community_name=community.name)

@login_required
@verification_required
def user_profile_page(request, username):
    selected_user = get_object_or_404(User, username=username)
    cache_key = f"posts"
    current_time = timezone.now()
    
    
    posts_all = cache.get(cache_key)
    if posts_all is None:
        print(f"\n Cache miss for key: {cache_key}. Querying database for posts.")
        posts_all = list(Post.objects.filter(user=selected_user).order_by('-created_at'))
        for post in posts_all:
            post.likes_count = post.likes.count()
            post.liked = post.likes.filter(user=request.user).exists()
            post.comments_count = post.comments.count()
            # 'can_edit' is set only if the selected user is the current user.
            post.can_edit = (selected_user == request.user and 
                             (current_time - post.created_at).total_seconds() <= 30 * 60)
        print(f"Set cache key: {cache_key} with {len(posts_all)} posts.")
        cache.set(cache_key, posts_all, timeout=600)
    else:
        print(f"\n Cache hit for key: {cache_key}. Updating dynamic fields for {len(posts_all)} posts.")
        for post in posts_all:
            post.likes_count = post.likes.count()
            post.liked = post.likes.filter(user=request.user).exists()
            post.comments_count = post.comments.count()
            post.can_edit = (selected_user == request.user and 
                             (current_time - post.created_at).total_seconds() <= 30 * 60)

    # Filter posts to only those that belong to the selected user.
    user_posts = [post for post in posts_all if post.user == selected_user]
    is_friend = selected_user in request.user.friends.all()
    return render(request, 'pages/user_profile.html', {
        'user': request.user,
        'user_profile': selected_user,
        'posts': user_posts,
        'is_friend': is_friend
    })

    
@login_required
@verification_required
def faq_view(request):
    """Render the FAQ page (requires login)."""
    return render(request, "pages/faq.html", {"user": request.user})

