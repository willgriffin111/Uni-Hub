from django.urls import path
from . import views
from .views import CreateCommunityView, CommunityJoinAPI, CommunityEditAPI, CommunityViewAPI, DeleteCommunityView

urlpatterns = [
    path('editcommunity/', views.CommunityEditAPI.as_view(), name='api-community-edit'),
    path('communitypost/', views.CommunityViewAPI.as_view(), name='communitypost'),
    path('communityjoin/', views.CommunityJoinAPI.as_view(), name='api-communityjoin'),
    path('community/', CreateCommunityView.as_view(), name="community-create"),
    path('community/<int:community_id>/delete/', DeleteCommunityView.as_view(), name="community-delete"),
]