from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class UserAuthTests(APITestCase):
    def setUp(self):
        # Set up common test data and URLs
        self.register_url = reverse('api-register')
        self.login_url = reverse('api-login')
        self.logout_url = reverse('api-logout')
        self.password_reset_url = reverse('api-password-reset')
        self.password_reset_confirm_url = reverse('api-password-reset-confirm')
        
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "strongpassword123",
            "first_name": "Test",
            "last_name": "User",
            "dob": "2000-01-01",
            "university": "Test University",
            "student_id": "S123456"
        }
        # Create a test user
        self.user = User.objects.create_user(**self.user_data)

    def test_registration(self):
        # Delete the test user to simulate a new registration.
        self.user.delete()
        response = self.client.post(self.register_url, data=self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_login(self):
        # Prepare login data and use URL-encoded content type
        login_data = {
            "username": self.user.username,
            "password": "strongpassword123"
        }
        response = self.client.post(
            self.login_url, 
            data=login_data, 
            content_type="application/x-www-form-urlencoded"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("redirect", response.data)

    def test_logout(self):
        # Log in using Django's session authentication
        self.client.login(username=self.user.username, password="strongpassword123")
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Optionally check that the session is cleared
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_password_reset(self):
        reset_data = {"email": self.user.email}
        response = self.client.post(self.password_reset_url, data=reset_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_password_reset_confirm(self):
        # Generate token and UID for the password reset confirmation test
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        new_password = "newStrongPassword!456"
        reset_confirm_data = {
            "uid": uid,
            "token": token,
            "new_password": new_password
        }
        response = self.client.post(self.password_reset_confirm_url, data=reset_confirm_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Refresh the user from DB and check that the password has been updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
