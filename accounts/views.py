from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import permissions
from .permissions import IsEditor

class LoginAPI(APIView):
    permission_classes = (permissions.AllowAny,) 
    
    def post(self, request):
        # Get credentials from POST or JSON payload
        username = request.POST.get("username") or request.data.get("username")
        password = request.POST.get("password") or request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"redirect": "/dashboard/"}, status=200)
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

class RegisterAPI(APIView):
    permission_classes = (permissions.AllowAny,) 

    def post(self, request):
        first_name = request.POST.get("first_name") or request.data.get("first_name")
        last_name = request.POST.get("surname") or request.data.get("surname")
        email = request.POST.get("email") or request.data.get("email")
        password = request.POST.get("password") or request.data.get("password")
        if User.objects.filter(username=email).exists():
            return JsonResponse({"error": "Email already registered"}, status=400)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        return JsonResponse({"message": "Registration successful"}, status=201)

class LogoutAPI(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        logout(request)
        return JsonResponse({"redirect": "/login/"}, status=200)
