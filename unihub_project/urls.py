from django.contrib import admin
from django.urls import path, include
from accounts.views import login_view, dashboard_view, logout_view, RegisterView, UserDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication Views
    path('accounts/login/', login_view, name="login"),
    path('accounts/dashboard/', dashboard_view, name="dashboard"),
    path('accounts/logout/', logout_view, name="logout"),

    # API Endpoints
    path('api/register/', RegisterView.as_view(), name="register"),
    path('api/user/', UserDetailView.as_view(), name="user-detail"),
    
    # path('accounts/', include('accounts.urls')),  # Include other authentication routes
]
