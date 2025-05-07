from django.db import models
from django.conf import settings

class Community(models.Model):
    """
    Represents a community created by an authorized user.
    
    Fields:
      - name: Unique community name.
      - description: A detailed description or 'about' page for the community.
      - created_by: The user who created the community.
      - contact_email: Email for contacting community leaders.
      - created_at: Timestamp when the community was created.
      - members: Many-to-many relationship to the User model for those who joined.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    community_image = models.ImageField(
        upload_to='community/images/', 
        null=False, 
        blank=False,
        default='community/images/default.png'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="owned_communities"
    )
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    community_private = models.BooleanField(default=False)
    
    tags = models.TextField(blank=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="joined_communities",
        blank=True
    )

    def __str__(self):
        return self.name
    
    def is_user_blocked(self, user):
        """Check if a user is blocked from this community."""
        return self.blocked_users.filter(user=user).exists()

ROLE_HIERARCHY = {
    'member': 1,
    'event_leader': 2,
    'community_leader': 3,
    'admin': 4
}

class CommunityRole(models.Model):
    """
    Defines the role of a user in a community.
    
    Role choices:
      - admin: Full control, can manage the community and sessions.
      - community_leader: Can help moderate posts community and events.
      - event_leader: can only create edit and delete events
      - member: Standard member can only make posts to community.
    
    Ensures a user can have only one role per community.
    """
    
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('event_leader', 'Event Leader'),
        ('community_leader', 'Community Leader'),
        ('admin', 'Admin'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="roles")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')

    class Meta:
        unique_together = ('user', 'community')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} in {self.community.name}"

    def has_permission(self, required_role):
        """Checks if the user has the required permission level or higher."""
        return ROLE_HIERARCHY[self.role] >= ROLE_HIERARCHY[required_role]
    
    
class CommunityBlock(models.Model):
    """
    Tracks users who are blocked from a specific community.
    
    Fields:
      - user: The user who is blocked.
      - community: The community from which they are blocked.
      - reason: Optional reason for blocking.
      - blocked_at: Timestamp of when the user was blocked.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_blocks")
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="blocked_users")
    reason = models.TextField(blank=True, null=True)
    blocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'community')

    def __str__(self):
        return f"{self.user.username} blocked from {self.community.name}"
    


class CommunityEvent(models.Model):
    """
    Represents an event within a community.
    
    Fields:
      - community: The community hosting the event.
      - title: Event title.
      - description: Detailed information about the event.
      - event_date: The date of the event.
      - event_time: The time of the event.
      - location: Physical or virtual location.
      - created_at: Timestamp when the event was created.
      - updated_at: Timestamp for last update.
    """
    community = models.ForeignKey(
        Community, 
        on_delete=models.CASCADE, 
        related_name="events"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_date = models.DateField()
    event_time = models.TimeField()
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    max_attendees = models.PositiveIntegerField(default=50)    
    requred_materials = models.TextField(blank=True)   #spelt wrong

    def __str__(self):
        return f"{self.title} - {self.event_date} ({self.community.name})"
    
    
class CommunityEventAttendance(models.Model):
    ATTENDANCE_CHOICES = [
        ('yes', 'Attending'),
        ('no', 'Not Attending'),
    ]

    event = models.ForeignKey(CommunityEvent, on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=3, choices=ATTENDANCE_CHOICES)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.status} for {self.event.title}"
