from django.urls import path
from . import views 

urlpatterns = [
    path('communitypost/', views.CommunityViewAPI.as_view(), name='communitypost'),

]
