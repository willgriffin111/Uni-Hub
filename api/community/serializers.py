from rest_framework import serializers
from django.contrib.auth import get_user_model
from api.community.models import Community

User = get_user_model()

class CommunitySerializer(serializers.ModelSerializer):
    # Show the creator's username (read-only)
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Community
        # Exclude created_by from being required (or make it read-only)
        fields = [
            'id',
            'name',
            'description',
            'contact_email',
            'created_at',
            'created_by_username',
            'community_image',
        ]
        read_only_fields = ['id', 'created_at', 'created_by_username']
from .models import Community

class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ['name', 'description', 'community_image', 'contact_email']
