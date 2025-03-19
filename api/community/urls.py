from django.urls import path
from . import views 

urlpatterns = [
    path('editcommunity/', views.CommunityEditAPI.as_view(), name='api-community-edit'),
    path('communitypost/', views.CommunityViewAPI.as_view(), name='communitypost'),
    path('communityjoin/', views.CommunityJoinAPI.as_view(), name='api-communityjoin'),
]
