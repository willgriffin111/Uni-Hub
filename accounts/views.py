from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import CustomUserSerializer, RegisterSerializer
from django.shortcuts import redirect
from . import emailopt
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import CustomUser  # Import your custom user model
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import status
from .emailopt import send_email_password_reset 
from django.utils.encoding import force_bytes
from django.conf import settings


from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

def get_user_by_username(request, username):
    try:
        user = CustomUser.objects.get(username=username)  # Get user by username
        return user
    except CustomUser.DoesNotExist:
        raise Http404("User not found")

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
            request.session['username'] = user.username
            if user.email_verified == True:
                return JsonResponse({"redirect": "/profile/"}, status=200)
            else:
                return JsonResponse({"redirect": "/accounts/api/verify/"}, status=200)
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
            user = authenticate(request, username=request.data['username'], password=request.data['password'])
        
            if user is not None:
                login(request, user)
                request.session.save()
                request.session['email'] = request.data['email']
                request.session['username'] = request.data['username']
                return JsonResponse({"message": "Regerstration successful"}, status=201)
            else:
                return JsonResponse({"error": "Invalid credentials"}, status=401)
        return JsonResponse(serializer.errors, status=400)
    
class VerifyAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = get_user_by_username(request, request.session['username'])
        email = user.email
        if not email:
            return JsonResponse({"error": "Email not provided"}, status=400)

        otp_code = emailopt.generate_otp(email)  # Generate OTP
        emailopt.send_otp_email(email, otp_code)
        print(otp_code)
        
        # Store OTP and expiration time in session
        expiration_time = timezone.now() + timedelta(minutes=10)  # OTP expires in 5 minutes
        request.session['otp_code'] = otp_code
        request.session['otp_expiration'] = expiration_time.isoformat()

        # Redirect to the verification page
        print("redirecting")
        return redirect('/VerifyEmail/')

    def post(self, request):
        otp_code = request.data.get("otp")
        otp_code_from_session = request.session.get('otp_code')
        otp_expiration_from_session = request.session.get('otp_expiration')
        
        if not otp_code_from_session or not otp_expiration_from_session:
            return JsonResponse({"message": "OTP not found or expired"}, status=400)

        # Use datetime.fromisoformat to parse the expiration time
        otp_expiration_time = datetime.fromisoformat(otp_expiration_from_session)
        
        # Check if OTP has expired
        if timezone.now() > otp_expiration_time:
            return JsonResponse({"message": "OTP has expired"}, status=400)

        # Get user and verify OTP
        user = get_user_by_username(request, request.session['username'])
        
        if otp_code == otp_code_from_session:
            # Set the email_verified field to True
            user.email_verified = True
            user.save()

            return JsonResponse({"message": "Verification successful"}, status=201)
        
        return JsonResponse({"message": "Verification unsuccessful"}, status=400)


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

User = get_user_model()

class PasswordResetAPI(APIView):
    """
    API endpoint to handle password reset requests.
    Sends an email with a reset link.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "No user with this email."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate token and UID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"http://localhost:8000/password-reset-confirm/?uid={uid}&token={token}"
        
        try:
            send_email_password_reset(email, reset_link)
        except Exception as e:
            return Response({"error": f"Error sending email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print(reset_link)
        return Response({"message": "Password reset link sent."}, status=status.HTTP_200_OK)

class PasswordResetConfirmAPI(APIView):
    """
    API endpoint to confirm password reset and update the password.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        
        if not uidb64 or not token or not new_password:
            return Response({"error": "UID, token, and new password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        return Response({"message": "Password successfully reset."}, status=status.HTTP_200_OK)
