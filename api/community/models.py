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
    
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="joined_communities",
        blank=True
    )

    def __str__(self):
        return self.name


class CommunityRole(models.Model):
    """
    Defines the role of a user in a community.
    
    Role choices:
      - admin: Full control, can manage the community and sessions.
      - moderator: Can help moderate posts and events.
      - member: Standard member.
    
    Ensures a user can have only one role per community.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="roles")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')

    class Meta:
        unique_together = ('user', 'community')
        verbose_name = "Community Role"
        verbose_name_plural = "Community Roles"

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} in {self.community.name}"


# ARE WE STILL GOING TO DO THIS? - WILL
# class VirtualSession(models.Model):
#     """
#     Represents a virtual or interactive session scheduled by community leaders.
    
#     Fields:
#       - community: The community hosting the session.
#       - title: Session title.
#       - description: Detailed info about the session.
#       - scheduled_at: DateTime when the session will start.
#       - duration_minutes: How long the session lasts (in minutes).
#       - session_link: URL for accessing the virtual session.
#       - created_at: Timestamp when the session was created.
#       - updated_at: Timestamp for last update.
#     """
#     community = models.ForeignKey(
#         Community, 
#         on_delete=models.CASCADE, 
#         related_name="virtual_sessions"
#     )
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     scheduled_at = models.DateTimeField()
#     duration_minutes = models.PositiveIntegerField(default=60)
#     session_link = models.URLField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.title} ({self.community.name})"


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
