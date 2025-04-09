# Redis Caching info



 When a page loads, the view first checks Redis for a cached list of posts on the redis container. If the cache exists (cache hit), it reuses the post content data and updates  fields such as like, like count, comment, comment count and the can edit flag. If the cache is missing (cache miss), it queries the database and stores them in Redis with a timeout of 10 minutes, and then renders the page.

 Redis is faster than querying the database because it holds the cached data in RAM. (download RAM chat)

 This is the home page loading using cache:

 ```python 
 @login_required
def home_page(request):

    cache_key = "posts"
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

    ... 
                    
    return render(request, 'pages/home_page.html', {
        'posts': posts,
        'user': request.user,
        'top_communities': top_communities,
        'events': upcoming_events,
        'suggestions': suggestions
    })
 ```

 ## Drawback

 This makes the website load quicker but becuase currently all the posts are saved to the cache if we had a shit ton of posts then storing all them localy uses a lot of memory. To solve this we could only cache chunks of posts instead of all of them. 