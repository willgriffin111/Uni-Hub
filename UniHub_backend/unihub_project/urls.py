from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views
from unihub_project.views import *


urlpatterns = [
    
    path('', views.home_page, name="index_page"),
    
    
    path('admin/', admin.site.urls),
    
    path('login/', views.login_view, name="login_page"),
    path('password-reset/', views.password_reset_view, name="password_reset_page"),
    path('password-reset-confirm/', views.password_reset_confirm_view, name="password_reset_confirm_page"),
    
    path('register/', views.register_view, name="register_page"),
    path('VerifyEmail/', views.Verify_view, name="Verify_page"),
    
    path('profile-edit/', views.profile_edit_view, name="profile_edit_page"),
    
    #homepage
    path('dashboard/', views.dashboard_view, name="dashboard_page"),
    path('profile/', views.profile_view, name="profile_page"),
    path('post/', views.post_view, name="post_page"),

    path('edit_post/<int:post_id>/', views.edit_post, name="edit_post"),
    
    path('edit_comment/<int:comment_id>/', views.edit_comment_view, name="edit_comment_page"),
    
    #comunities
    path('create-community/', community_list_view, name='community_create'),
    path('communities/<str:community_name>/', views.community_view, name="community_page"),
    path('edit_community/<str:community_name>/', views.community_edit_view, name="community_edit_page"),
    path('manage_community/<str:community_name>/', views.community_manage_view, name="community_manage_page"),
    
    
    path('search/', views.search_view, name='search_page'),
    # Include API endpoints from the accounts app
    path('accounts/', include('api.accounts.urls')),  # Mount the accounts API
    path('api/post/', include('api.posts.urls')),  # Mount the posts API
    path('api/', include('api.posts.urls')),    # this is needed for search functions
    path('api/community/', include('api.community.urls')),  # Mount the community API

    
    
    # Our new community detail route:
    path('community/<str:community_name>/', views.community_view, name='community_page'),
    path('community/<str:community_name>/', community_view, name='community_page'),
    path('community/create/', community_create_page, name='community_create_page'),
    path('community/create/', views.community_create_page, name='community_create_page'),
    
    path('community/event/<int:event_id>/edit/', event_edit_view, name='event_edit_page'),
    
    path('userprofile/<str:username>/', user_profile_page, name='user-profile-page'),



    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

