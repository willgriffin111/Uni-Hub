from django.urls import path
from . import views 

urlpatterns = [
    path('communitypost/', views.community_view_api.as_view(), name='communitypost'),

]
