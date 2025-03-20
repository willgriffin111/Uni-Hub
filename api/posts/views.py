from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from .models import Post
from .serializers import PostSerializer, LikeSerializer, CommentSerializer
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.response import Response
from .models import Like, Post, Comment
from django.contrib.auth import get_user_model
from django.db.models import Q
from api.community.models import Community

User = get_user_model()

class PostListCreateViewAPI(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        image = self.request.FILES.get("image")  # Get uploaded image file
        serializer.save(user=self.request.user, image=image)

    def get_serializer_context(self):
        """Ensures that the serializer gets the request context."""
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

        
class PostEditAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request):
        post_id = request.data.get('post_id')
        post = get_object_or_404(Post, id=post_id, user=request.user)  # Ensure user owns the post

        post.title = request.data.get("title", post.title)
        post.content = request.data.get("content", post.content)
        post.tags = request.data.get("tags", post.tags)

        if "image" in request.FILES:
            if post.image:
                 post.image.delete(save=False)  # Deletes from /media/
            post.image = request.FILES["image"]

        post.save()
        return Response(PostSerializer(post).data, status=status.HTTP_200_OK)
    
class PostDeleteAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, user=request.user)
        post.image.delete(save=False) 
        post.delete()
        # return redirect('post_list')
        return redirect('index_page')


class LikePostAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()  # Unlike if already liked
            liked = False
            print("Unliked")
        else:
            liked = True
            print("Liked")

        return Response({
            "liked": liked,
            "like_count": post.likes.count()
        }, status=status.HTTP_200_OK)


class CommentPostAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        parent_id = request.data.get("parent_id")  # Get parent comment ID if it's a reply

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            parent_comment = None
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)  # Get parent comment if replying

            serializer.save(user=request.user, post=post, parent=parent_comment)  # Save as reply if parent exists
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class CommentDeleteAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)  # Ensure user owns the comment
        comment.delete()
        return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class CommentEditAPI(APIView):
    """API endpoint to update a comment."""
    
    def put(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)  # Ensure only the owner can edit
        new_content = request.data.get("content", "").strip()

        if not new_content:
            return Response({"error": "Content cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        comment.content = new_content
        comment.save()
        return Response({"message": "Comment updated successfully", "content": new_content}, status=status.HTTP_200_OK)


"""
This API view allows authenticated users to search for other users by username
"""
class UserSearchAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]  

    def get(self, request):
        query = request.GET.get('query', None)
        if query:
            user_profile_list = User.objects.filter(    # filters based on username, provided from search query
                Q(username__icontains=query)
            ).exclude(id=request.user.id) # dont't include the current user

            users_data = [
                {
                    "username": user.username, 
                    "user_type": user.user_type,
                    "university": user.university
                } 
                for user in user_profile_list
            ]
            return Response(users_data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No search query provided."}, status=status.HTTP_400_BAD_REQUEST)
