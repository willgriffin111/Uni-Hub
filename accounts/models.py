from django.contrib.auth.models import AbstractUser
from django.db import models


#  THIS IS A CUSTOM USER MODEL THAT EXTENDS THE DJANGO USER MODEL TO ADD DOB, UNIVERSITY, AND STUDENT ID FIELDS - WILL
class CustomUser(AbstractUser):
    dob = models.DateField(null=True, blank=True)
    university = models.CharField(max_length=255, null=True, blank=True)
    student_id = models.CharField(max_length=50, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    #all possible user types accepted
    USER_TYPES = [
        ('student', 'Student'),
        ('com_leader', 'Com_leader'),
        ('evt_leader', 'Evt_leader'),
        ('admin', 'Admin'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')

    def __str__(self):
        return self.username

