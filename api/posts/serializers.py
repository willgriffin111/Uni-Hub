from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'user', 'title', 'content', 'image', 'tags', 'created_at']
        read_only_fields = ['id', 'user', 'created_at', 'image']
