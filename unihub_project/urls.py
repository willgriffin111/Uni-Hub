from django.contrib import admin
from django.urls import path, include
from .views import login_view, register_view, dashboard_view, Verify_view, profile_view, password_reset_view
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('login/', login_view, name="login_page"),
    path('password-reset/', views.password_reset_view, name="password_reset_page"),
    path('password-reset-confirm/', views.password_reset_confirm_view, name="password_reset_confirm_page"),
    
    path('register/', register_view, name="register_page"),
    path('VerifyEmail/', Verify_view, name="Verify_page"),
    
    path('dashboard/', dashboard_view, name="dashboard_page"),
    path('profile/', profile_view, name="profile_page"),
    # Include API endpoints from the accounts app
    path('accounts/', include('accounts.urls')),
    
    

]

