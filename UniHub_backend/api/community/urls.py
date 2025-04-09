from django.urls import path
from . import views
from .views import *
from .views import CommunitySearchAPI

urlpatterns = [
    path('editcommunity/', views.CommunityEditAPI.as_view(), name='api-community-edit'),
    path('communityjoin/', views.CommunityJoinAPI.as_view(), name='api-communityjoin'),
    path('community/', CreateCommunityView.as_view(), name="community-create"),
    path('community/<int:community_id>/delete/', DeleteCommunityView.as_view(), name="community-delete"),
    
    
    path('community/<int:community_id>/events/create/', CommunityEventCreateAPI.as_view()),
    path('community/<int:community_id>/events/', CommunityEventListAPI.as_view()),
    
    path('events/<int:event_id>/', CommunityEventDetailAPI.as_view()),
    path('events/<int:event_id>/attendance/', MarkAttendanceAPI.as_view()),
    path('events/<int:event_id>/attendees/', AttendanceListAPI.as_view()),
    path('events/<int:event_id>/delete/', CommunityEventDeleteAPI.as_view()),
    path('events/<int:event_id>/edit/', CommunityEventEditAPI.as_view(), name='event_edit_api'),
    
    path('search/', CommunitySearchAPI.as_view(), name='api-community-search'),
    
    path('api/community/promote/', PermoteMemberAPI.as_view(), name='api-promote-member'),
    path('api/community/demote/', DemoteMemberAPI.as_view(), name='api-demote-member'),
    
    path('api/community/block/', BlockMemberAPI.as_view(), name='api-block-member'),
    path('api/community/unblock/', UnBlockMemberAPI.as_view(), name='api-unblock-member'),
]