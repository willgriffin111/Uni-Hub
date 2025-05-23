from django.urls import path
from . import views 
from .views import TagSearchAPI

urlpatterns = [
    path('post/', views.PostListCreateViewAPI.as_view(), name='post-list-create'),
    path('post-edit/', views.PostEditAPI.as_view(), name="edit_post_api"),
    path('delete-post/<int:post_id>/', views.PostDeleteAPI.as_view(), name="delete_post"),
    
    path('like-post/<int:post_id>/', views.LikePostAPI.as_view(), name="like_post"),
    
    path('comment-post/<int:post_id>/', views.CommentPostAPI.as_view(), name="comment_post"),
    path('delete-comment/<int:comment_id>/', views.CommentDeleteAPI.as_view(), name="delete_comment"), 
    path('edit-comment/<int:comment_id>/', views.CommentEditAPI.as_view(), name="edit_comment"),  

    path('search/users/', views.UserSearchAPI.as_view(), name="search_users"),
    
    path('tags/search/', TagSearchAPI.as_view(), name='api-tag-search'),
    
     path('delete-post/<int:post_id>/', views.PostDeleteAPI.as_view(), name="delete_post"),
     path('post-delete-community/<int:post_id>/<int:community_id>/', views.CommunityPostDeleteAPI.as_view(), name='community-delete-post')
]
