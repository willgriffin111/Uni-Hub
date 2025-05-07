from django.contrib import admin
from .models import Post, Like, Comment

class PostAdmin(admin.ModelAdmin):
    exclude = ()
    list_display = ('title', 'user', 'community', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'tags', 'user__username')
    list_filter = ('created_at', 'community')

class LikeAdmin(admin.ModelAdmin):
    exclude = ()
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'post__title')
    list_filter = ('created_at',)

class CommentAdmin(admin.ModelAdmin):
    exclude = ()
    list_display = ('user', 'post', 'created_at')
    search_fields = ('content', 'user__username', 'post__title')
    list_filter = ('created_at',)

admin.site.register(Post, PostAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Comment, CommentAdmin)
