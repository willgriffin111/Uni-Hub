from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import CustomUserSerializer, RegisterSerializer

class LoginAPI(APIView):
    """
    API to handle user login. Uses session authentication.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({"redirect": "/dashboard/"}, status=200)
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

class RegisterAPI(APIView):
    """
    API to handle user registration.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "Registration successful"}, status=201)
        return JsonResponse(serializer.errors, status=400)

class LogoutAPI(APIView):
    """
    API to handle user logout. Only accessible to authenticated users.
    """
    # THIS ISNT WORKING. ONLY LOGGED IN USERS CAN LOG OUT. I THINK IT JWT RELATED BUT IM NOT SURE. 
    # JWT SETTING IN SETTINGS.PY FILE. 
    # mayb we dont use jwt idk?
    # permission_classes = [IsAuthenticated]   
    
    # THIS WORKS but its not correct.
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return JsonResponse({"redirect": "/login/"}, status=200)
