from rest_framework import generics, permissions
from .models import Post
from .serializers import PostSerializer

class PostListCreateViewAPI(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        print(self.request.user)
        serializer.save(user=self.request.user)
