from django.urls import path
from . import views
from .views import *

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
]