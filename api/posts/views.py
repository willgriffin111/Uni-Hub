from rest_framework import generics, permissions
from .models import Post
from .serializers import PostSerializer

class PostListCreateViewAPI(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        image = self.request.FILES.get("image")  # Get uploaded image file
        # Save the post with the image and the authenticated user
        serializer.save(user=self.request.user, image=image)