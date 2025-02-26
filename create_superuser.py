

# I MADE THIS SO A SUPERUSER CAN BE CREATED AUTOMATICALLY WHEN THE DOCKER CONTAINER IS STARTED - WILL

import os
import django
from django.contrib.auth import get_user_model

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unihub_project.settings")
django.setup()

User = get_user_model()

# Create superuser if it doesn't exist
if not User.objects.filter(username="root").exists():
    User.objects.create_superuser("root", "root@unihub.com", "root")
    print("Superuser created: root / root")
else:
    print("Superuser already exists")
