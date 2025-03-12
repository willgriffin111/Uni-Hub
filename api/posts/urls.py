from django.urls import path
from . import views 

urlpatterns = [
    path('post/', views.PostListCreateViewAPI.as_view(), name='post-list-create'),
    path('post-edit/', views.PostEditAPI.as_view(), name="edit_post_api"),
    path('delete-post/<int:post_id>/', views.PostDeleteAPI.as_view(), name="delete_post"),
]
