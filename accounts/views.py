from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import permissions
from .models import CustomUser
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
        
        # Extract additional fields correctly
        dob = request.POST.get("dob") or request.data.get("dob")
        university = request.POST.get("university") or request.data.get("university")
        student_id = request.POST.get("student_id") or request.data.get("student_id")
        
        if CustomUser.objects.filter(username=email).exists():
            return JsonResponse({"error": "Email already registered"}, status=400)
        
        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            university=university,
            student_id=student_id
        )
        return JsonResponse({"message": "Registration successful"}, status=201)

class LogoutAPI(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        logout(request)
        return JsonResponse({"redirect": "/login/"}, status=200)
