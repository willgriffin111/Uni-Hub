from django.contrib import admin
from .models import (
    Community, 
    CommunityRole, 
    CommunityEvent, 
    CommunityEventAttendance
)

class CommunityAdmin(admin.ModelAdmin):
    exclude = ()
    list_display = ('name', 'created_by', 'contact_email', 'created_at')
    search_fields = ('name', 'description', 'contact_email')
    list_filter = ('created_at',)

class CommunityRoleAdmin(admin.ModelAdmin):
    exclude = ()
    list_display = ('user', 'community', 'role')
    search_fields = ('user__username',)
    list_filter = ('role', 'community')

class CommunityEventAdmin(admin.ModelAdmin):
    exclude = ()
    list_display = ('title', 'community', 'event_date', 'event_time')
    search_fields = ('title', 'description')
    list_filter = ('event_date', 'community')

class CommunityEventAttendanceAdmin(admin.ModelAdmin):
    exclude = ()
    list_display = ('user', 'event', 'status')
    search_fields = ('user__username', 'event__title')
    list_filter = ('status', 'event')

admin.site.register(Community, CommunityAdmin)
admin.site.register(CommunityRole, CommunityRoleAdmin)
admin.site.register(CommunityEvent, CommunityEventAdmin)
admin.site.register(CommunityEventAttendance, CommunityEventAttendanceAdmin)
