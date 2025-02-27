from django.contrib.auth.models import AbstractUser
from django.db import models

#  THIS IS A CUSTOM USER MODEL THAT EXTENDS THE DJANGO USER MODEL TO ADD DOB, UNIVERSITY, AND STUDENT ID FIELDS - WILL
class CustomUser(AbstractUser):
    dob = models.DateField(null=True, blank=True)
    university = models.CharField(max_length=255, null=True, blank=True)
    student_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.username
