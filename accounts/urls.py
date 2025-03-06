from django.urls import path
from .views import LoginAPI, RegisterAPI, LogoutAPI, VerifyAPI, PasswordResetAPI, PasswordResetConfirmAPI
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('api/login/', LoginAPI.as_view(), name="api-login"),
    path('api/register/', RegisterAPI.as_view(), name="api-register"),
    path('api/verify/', VerifyAPI.as_view(), name="api-verify"),
    path('api/logout/', LogoutAPI.as_view(), name="api-logout"),
    
    path('api/password-reset/', PasswordResetAPI.as_view(), name="api-password-reset"),
    path('api/password-reset-confirm/', PasswordResetConfirmAPI.as_view(), name="api-password-reset-confirm"),
]

