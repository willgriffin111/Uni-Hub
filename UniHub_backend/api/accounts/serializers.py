from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for returning user data."""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name',
            'last_name', 'dob', 'university', 'student_id', 'user_type', 'address',
            'course', 'year_of_ study', 'intrests', 
            
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for registering a new user."""

    password = serializers.CharField(write_only=True, required=True)  # This is so the password isn't returned in the response.

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name',
            'last_name', 'dob', 'university', 'student_id', 'user_type', 'address',
            'profile_picture',
            'bio',
            'gender',
            # 'course', 'year_of_ study', 'intrests'
        ]

    def create(self, validated_data):
        """Creates a new user with a properly hashed password."""
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),  
            dob=validated_data.get('dob'),
            university=validated_data.get('university', ''),
            student_id=validated_data.get('student_id', ''),
            user_type=validated_data.get('user_type', 'student'),
            address=validated_data.get('address', ''),
            course=validated_data.get('course', ''),
            year_of_study=validated_data.get('year_of_study', ''),
            intrests=validated_data.get('intrests', ''),
        )
