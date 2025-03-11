from django.urls import path
from .views import PostListCreateViewAPI

urlpatterns = [
    path('test/', PostListCreateViewAPI.as_view(), name='post-list-create'),
]
