from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Display user details including email_verified
    list_display = ['id', 'username', 'email', 'first_name', 'last_name', 'dob', 'university', 'student_id', 'user_type', 'email_verified']
    list_filter = ['user_type', 'university', 'dob', 'email_verified']  # Add email_verified to filter options

    # Allow editing `email_verified` in the user detail view
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('dob', 'university', 'student_id', 'user_type', 'email_verified')}),
    )

    # Allow selecting `email_verified` when creating a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('dob', 'university', 'student_id', 'user_type', 'email_verified')}),
    )

    # Enable searching users by username, email, or university
    search_fields = ['username', 'email', 'university']
    ordering = ['id']

admin.site.register(CustomUser, CustomUserAdmin)
