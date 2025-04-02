import os
import requests
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.files.storage import default_storage
from django.conf import settings
from django.http import JsonResponse, Http404
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CustomUserSerializer, RegisterSerializer
from accounts.models import CustomUser

User = get_user_model()


def get_user_by_username(request, username):
    try:
        user = CustomUser.objects.get(username=username)
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
            if user.email_verified:
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
                return JsonResponse({"message": "Registration successful"}, status=201)
            else:
                return JsonResponse({"error": "Invalid credentials"}, status=401)
        return JsonResponse(serializer.errors, status=400)


class VerifyAPI(APIView):
    """
    API to verify a user's email by sending and validating an OTP.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        user = get_user_by_username(request, request.session.get('username'))
        email = user.email
        if not email:
            return JsonResponse({"error": "Email not provided"}, status=400)

        # Call the notification service to send OTP
        try:
            response = requests.post(
                "http://notification:8001/send-otp",
                json={"email": email},
                timeout=5
            )
            if response.status_code == 200:
                otp_code = response.json().get("otp")
            else:
                return JsonResponse({"error": "Failed to send OTP"}, status=500)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        # Store OTP and expiration time in session (OTP expires in 10 minutes)
        expiration_time = timezone.now() + timedelta(minutes=10)
        request.session['otp_code'] = otp_code
        request.session['otp_expiration'] = expiration_time.isoformat()

        return redirect('/VerifyEmail/')

    def post(self, request):
        otp_code = request.data.get("otp")
        otp_code_from_session = request.session.get('otp_code')
        otp_expiration_from_session = request.session.get('otp_expiration')

        if not otp_code_from_session or not otp_expiration_from_session:
            return JsonResponse({"message": "OTP not found or expired"}, status=400)

        otp_expiration_time = datetime.fromisoformat(otp_expiration_from_session)
        if timezone.now() > otp_expiration_time:
            return JsonResponse({"message": "OTP has expired"}, status=400)

        user = request.user
        if otp_code == otp_code_from_session:
            user.email_verified = True
            user.save()
            return JsonResponse({"message": "Verification successful"}, status=201)

        return JsonResponse({"message": "Verification unsuccessful"}, status=400)


class LogoutAPI(APIView):
    """
    API to handle user logout. Only accessible to authenticated users.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return JsonResponse({"redirect": "/login/"}, status=200)


class PasswordResetAPI(APIView):
    """
    API endpoint to handle password reset requests.
    Sends an email with a reset link via the notification service.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "No user with this email."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate token and UID for password reset
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"http://localhost:8000/password-reset-confirm/?uid={uid}&token={token}"

        # Call the notification service to send the reset email
        try:
            response = requests.post(
                "http://notification:8001/send-reset-link",
                json={"email": email, "link": reset_link},
                timeout=5
            )
            if response.status_code != 200:
                return Response({"error": "Failed to send reset email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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


class ProfileUpdateAPI(APIView):
    """
    API endpoint for updating user profile information.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request):
        user = request.user
        data = request.data

        if "profile_picture" in request.FILES:
            if user.profile_picture and user.profile_picture.name != 'profile_pics/user-image.png':
                user.profile_picture.delete(save=False)
            user.profile_picture = request.FILES["profile_picture"]

        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)

        # Handle date of birth correctly
        dob = data.get('dob')
        user.dob = dob if dob and dob.strip() != '' else None

        user.university = data.get('university', user.university)
        user.student_id = data.get('student_id', user.student_id)
        user.bio = data.get('bio', user.bio)
        user.gender = data.get('gender', user.gender)

        try:
            user.save()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Profile updated successfully",
            "data": {
                "profile_picture": user.profile_picture.url if user.profile_picture else None,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "dob": user.dob,
                "university": user.university,
                "student_id": user.student_id,
                "bio": user.bio,
                "gender": user.gender,
            }
        }, status=status.HTTP_200_OK)


class DeleteAccountAPI(APIView):
    """
    API endpoint to delete a user account and associated profile picture.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        try:
            if user.profile_picture:
                if os.path.exists(user.profile_picture.path):
                    os.remove(user.profile_picture.path)
            user.delete()
            return Response({"message": "Account and profile picture deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RemoveProfilePictureAPI(APIView):
    """
    API endpoint to remove a user's profile picture and reset it to a default image.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        default_pic = 'profile_pics/user-image.png'
        if user.profile_picture:
            if user.profile_picture.name != default_pic:
                if default_storage.exists(user.profile_picture.name):
                    default_storage.delete(user.profile_picture.name)
            user.profile_picture = default_pic
            user.save()
            return Response({"message": "Profile picture removed and reset to default."}, status=status.HTTP_200_OK)
        return Response({"error": "No profile picture found."}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPI(APIView):
    """
    API endpoint to retrieve the current user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)


class FriendAddAPI(APIView):
    """
    API endpoint to add a friend.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        if not username:
            return Response({'success': False, 'message': 'No username provided.'}, status=status.HTTP_400_BAD_REQUEST)
        if username == request.user.username:
            return Response({'success': False, 'message': "You cannot add yourself as a friend."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            friend = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'success': False, 'message': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        if friend in request.user.friends.all():
            return Response({'success': False, 'message': 'Already friends.'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.friends.add(friend)
        return Response({'success': True, 'message': 'Friend added successfully.'})


class FriendRemoveAPI(APIView):
    """
    API endpoint to remove a friend.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        if not username:
            return Response({'success': False, 'message': 'No username provided.'}, status=status.HTTP_400_BAD_REQUEST)
        if username == request.user.username:
            return Response({'success': False, 'message': "You cannot remove yourself."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            friend = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'success': False, 'message': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        if friend not in request.user.friends.all():
            return Response({'success': False, 'message': 'Not friends.'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.friends.remove(friend)
        return Response({'success': True, 'message': 'Friend removed successfully.'})
