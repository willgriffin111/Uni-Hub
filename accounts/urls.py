from django.urls import path
from .views import LoginAPI, RegisterAPI, LogoutAPI

urlpatterns = [
    path('api/login/', LoginAPI.as_view(), name="api-login"),
    path('api/register/', RegisterAPI.as_view(), name="api-register"),
    path('api/logout/', LogoutAPI.as_view(), name="api-logout"),
]
