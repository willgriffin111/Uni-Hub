from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['id', 'username', 'email', 'first_name', 'last_name', 'dob', 'university', 'student_id']
    # Add custom fields to the fieldsets so they're editable in the admin.
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('dob', 'university', 'student_id')}),
    )
    # Add custom fields when creating a new user via the admin.
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('dob', 'university', 'student_id')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
