from django.urls import path
from .views import PostListCreateViewAPI

urlpatterns = [
    path('post/', PostListCreateViewAPI.as_view(), name='post-list-create'),
]
