from rest_framework import serializers
from .models import Post, Like, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']



class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    liked = serializers.SerializerMethodField()  # Determines if the user has liked the post

    class Meta:
        model = Post
        fields = ['id', 'user', 'title', 'content', 'image', 'tags', 'created_at', 'likes_count', 'liked']

    def get_liked(self, obj):
        """Returns True if the current user has liked this post."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            print("Already Liked")
            return obj.likes.filter(user=request.user).exists()
        return False
