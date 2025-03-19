from django.urls import path
from .views import CreateCommunityView

urlpatterns = [
    path('editcommunity/', views.CommunityEditAPI.as_view(), name='api-community-edit'),
    path('communitypost/', views.CommunityViewAPI.as_view(), name='communitypost'),
    path('communityjoin/', views.CommunityJoinAPI.as_view(), name='api-communityjoin'),
    path('community/', CreateCommunityView.as_view(), name="community-create"),
]
