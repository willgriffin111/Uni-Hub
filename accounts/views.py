from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserSerializer

def login_view(request):
    """Handles user login."""
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect("dashboard")  # Redirect to dashboard after login
        else:
            return render(request, "pages/login.html", {"error": "Invalid username or password."})

    return render(request, "pages/login.html")


@login_required
def dashboard_view(request):
    """Displays user dashboard (requires login)."""
    return render(request, "pages/dashboard.html", {"user": request.user})


def logout_view(request):
    """Handles user logout."""
    logout(request)
    return redirect("login")  # Redirect to login page after logout


class RegisterView(generics.CreateAPIView):
    """API endpoint for user registration."""
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class UserDetailView(generics.RetrieveAPIView):
    """API endpoint to retrieve details of the logged-in user."""
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
