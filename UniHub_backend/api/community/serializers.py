from rest_framework import serializers
from django.contrib.auth import get_user_model
from api.community.models import Community, CommunityEvent, CommunityEventAttendance, CommunityRole

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
            'tags',
        ]
        read_only_fields = ['id', 'created_at', 'created_by_username']
from .models import Community

class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ['name', 'description', 'community_image','tags' ,'contact_email']

class CommunityEventSerializer(serializers.ModelSerializer):
    is_user_attending = serializers.SerializerMethodField()
    attendance_count = serializers.SerializerMethodField()
    attendees = serializers.SerializerMethodField()

    class Meta:
        model = CommunityEvent
        fields = [
            'id', 'title', 'description', 'event_date', 'event_time', 
            'location', 'attendance_count', 'attendees', 'is_user_attending'
        ]

    def get_is_user_attending(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.attendances.filter(user=request.user, status='yes').exists()
        return False

    def get_attendance_count(self, obj):
        return obj.attendances.filter(status='yes').count()

    def get_attendees(self, obj):
        attendees = obj.attendances.filter(status='yes')
        attendee_usernames = []
        for att in attendees:
            if att.user and att.user.username:
                attendee_usernames.append(att.user.username)
        return attendee_usernames

class CommunityEventAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityEventAttendance
        fields = ['event', 'user', 'status']
        
        



class CommunityRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityRole
        fields = ['role']
    
    def validate_role(self, value):
        """Ensure the new role is a valid choice."""
        valid_roles = [choice[0] for choice in CommunityRole.ROLE_CHOICES]
        if value not in valid_roles:
            raise serializers.ValidationError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        return value

    def update(self, instance, validated_data):
        """Update the role of a CommunityRole instance."""
        instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance