from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from .models import Post
from .serializers import PostSerializer
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.response import Response

class PostListCreateViewAPI(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        image = self.request.FILES.get("image")  # Get uploaded image file
        # Save the post with the image and the authenticated user
        serializer.save(user=self.request.user, image=image)
        
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
        return redirect('post_list')