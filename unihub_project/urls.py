from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('login/', views.login_view, name="login_page"),
    path('password-reset/', views.password_reset_view, name="password_reset_page"),
    path('password-reset-confirm/', views.password_reset_confirm_view, name="password_reset_confirm_page"),
    
    path('register/', views.register_view, name="register_page"),
    path('VerifyEmail/', views.Verify_view, name="Verify_page"),
    
    path('dashboard/', views.dashboard_view, name="dashboard_page"),
    path('profile/', views.profile_view, name="profile_page"),
    path('post/', views.post_view, name="post_page"),
    path('posts/', views.post_list, name="post_list"),
    path('edit_post/<int:post_id>/', views.edit_post, name="edit_post"),
    
    path('edit_comment/<int:comment_id>/', views.edit_comment_view, name="edit_comment_page"),
    # Include API endpoints from the accounts app
    path('accounts/', include('accounts.urls')),  # Mount the accounts API
    path('api/post/', include('api.posts.urls')),  # Mount the posts API

    
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

