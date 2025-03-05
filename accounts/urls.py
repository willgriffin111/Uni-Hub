from django.urls import path
from .views import LoginAPI, RegisterAPI, LogoutAPI, VerifyAPI

urlpatterns = [
    path('api/login/', LoginAPI.as_view(), name="api-login"),
    path('api/register/', RegisterAPI.as_view(), name="api-register"),
    path('api/verify/', VerifyAPI.as_view(), name="api-verify"),
    path('api/logout/', LogoutAPI.as_view(), name="api-logout"),
]
