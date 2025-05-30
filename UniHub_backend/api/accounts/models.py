from django.contrib.auth.models import AbstractUser
from django.db import models


#  THIS IS A CUSTOM USER MODEL THAT EXTENDS THE DJANGO USER MODEL TO ADD DOB, UNIVERSITY, AND STUDENT ID FIELDS - WILL
class CustomUser(AbstractUser):
    dob = models.DateField(null=True, blank=True)
    university = models.CharField(max_length=255, null=True, blank=True)
    student_id = models.CharField(max_length=50, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    friends = models.ManyToManyField('self', blank=True, symmetrical=True)
    #all possible user types accepted
    USER_TYPES = [
        ('student', 'Student'),
        ('com_leader', 'Com_leader'),
        ('evt_leader', 'Evt_leader'),
        ('admin', 'Admin'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')
    
    profile_picture = models.ImageField(upload_to="profile_pics/", default='profile_pics/user-image.png',null=False, blank=False)
    bio = models.TextField(null=True, blank=True)
    gender = models.CharField(
        max_length=10, 
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")], 
        null=True, 
        blank=True
    )
    address = models.CharField(max_length=255, null=True, blank=True)
    
    course = models.CharField(max_length=255, null=True, blank=True)
    year_of_study = models.CharField(max_length=50, null=True, blank=True)
    intrests = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.username

