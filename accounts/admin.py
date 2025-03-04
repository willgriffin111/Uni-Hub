from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Display user details including user_type
    list_display = ['id', 'username', 'email', 'first_name', 'last_name', 'dob', 'university', 'student_id', 'user_type']
    list_filter = ['user_type', 'university', 'dob']

    # Allow editing `user_type` in the user detail view
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('dob', 'university', 'student_id', 'user_type')}),
    )

    # Allow selecting `user_type` when creating a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('dob', 'university', 'student_id', 'user_type')}),
    )

    # Enable searching users by username, email, or university
    search_fields = ['username', 'email', 'university']
    ordering = ['id']

admin.site.register(CustomUser, CustomUserAdmin)
