# I MADE THIS SO A SUPERUSER CAN BE CREATED AUTOMATICALLY WHEN THE DOCKER CONTAINER IS STARTED - WILL
# I UPDATED THIS 20/3/2025 TO INCLUDE DEFAULT VALUES FOR THE NEW FIELDS - WILL

import os
import django
from django.contrib.auth import get_user_model

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unihub_project.settings")
django.setup()

User = get_user_model()

DEFAULTS = {
    "dob": "2000-01-01",  
    "university": "Default University",
    "student_id": "000000",
    "bio": "This is a default bio.",
    "gender": "other",
    "profile_picture": None,  
}

# Create superuser if it doesn't exist
if not User.objects.filter(username="root").exists():
    superuser = User.objects.create_superuser("root", "root@unihub.com", "root")
    
    # Set default values for missing fields
    for field, value in DEFAULTS.items():
        setattr(superuser, field, value)
    
    superuser.save()
    print("Superuser created: root / root with full profile fields")
else:
    print("Superuser already exists")
