from django.contrib import admin
from django.urls import path, include
from .views import login_view, register_view, dashboard_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name="login_page"),
    path('register/', register_view, name="register_page"),
    path('dashboard/', dashboard_view, name="dashboard_page"),
    # Include API endpoints from the accounts app
    path('accounts/', include('accounts.urls')),
]
