from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect("dashboard")  # Redirect to dashboard
        else:
            return render(request, "pages/login.html", {"error": "Invalid credentials."})

    return render(request, "pages/login.html")


@login_required
def dashboard_view(request):
    return render(request, "pages/dashboard.html", {"user": request.user})


def logout_view(request):
    logout(request)
    return redirect("login")  # Redirect to login page after logout

def register_view(request):
    return render(request, "pages/register.html")
