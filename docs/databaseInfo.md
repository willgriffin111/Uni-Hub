# The databse

This project uses Django’s ORM (Object–relational mapping) to manage the database. Rather than writing SQL (what we did before), we define our schema using Django models. Django automatically creates the tables and handles join tables for many-to-many relationships. 

At the bottom is the sql code too as beause i thought it was easier to write the sql and turn it into django code

Below is an overview of the main models for Uni Hub.

## Accounts
```python

class CustomUser(AbstractUser):
    dob = models.DateField(null=True, blank=True)
    university = models.CharField(max_length=255, null=True, blank=True)
    student_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.username
```


## Communities
```python
from django.db import models
from django.conf import settings  

class Community(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_communities'
    )
    # Many-to-Many relationship: a user can belong to many communities,
    # and a community can have many users.
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='communities'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

```

## Events
```python

from django.db import models
from django.conf import settings
from communities.models import Community

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events'
    )
    # An event may be associated with a community (or not)
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='events',
        null=True,
        blank=True
    )
    # Users who RSVP to attend the event
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='attended_events',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

```

## Posts
```python
from django.db import models
from django.conf import settings
from communities.models import Community

class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    # A post can be associated with a community? Optional
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='posts',
        null=True,
        blank=True
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Show first 50 characters of the post for preview.
        return f"{self.author.username}: {self.content[:50]}"

```

## Notifications

```python
from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {'Read' if self.is_read else 'Unread'}"

```


# SQL CODE:

```sql
-- USERS TABLE (Custom User Model)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    dob DATE,
    university VARCHAR(255),
    student_id VARCHAR(20) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- COMMUNITIES TABLE
CREATE TABLE communities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by INT REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- COMMUNITY MEMBERSHIP TABLE (Many-to-Many Relationship)
CREATE TABLE community_membership (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    community_id INT REFERENCES communities(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, community_id)  -- Ensures a user can't join the same community twice
);

-- EVENTS TABLE
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    time TIME NOT NULL,
    location VARCHAR(255),
    created_by INT REFERENCES users(id) ON DELETE CASCADE,
    community_id INT REFERENCES communities(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- EVENT ATTENDEES TABLE (Many-to-Many Relationship)
CREATE TABLE event_attendees (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    event_id INT REFERENCES events(id) ON DELETE CASCADE,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, event_id)  -- Ensures a user can't register for the same event twice
);

-- POSTS TABLE
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    author_id INT REFERENCES users(id) ON DELETE CASCADE,
    community_id INT REFERENCES communities(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NOTIFICATIONS TABLE
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

```

