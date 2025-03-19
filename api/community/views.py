from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Community, CommunityRole
from .serializers import CommunitySerializer

class CreateCommunityView(generics.CreateAPIView):
    """
    API endpoint to create a new community.
    The creator is automatically set as the community's owner,
    is added as a member, and is assigned the admin role.
    """
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Validate incoming data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save community with the current user as creator
        community = serializer.save(created_by=request.user)
        
        # Add the creator as a member and assign them as admin
        community.members.add(request.user)
        CommunityRole.objects.create(user=request.user, community=community, role='admin')
        
        # Build a redirect URL using the community name (assuming it’s unique)
        redirect_url = f"/community/{community.name}/"
        
        # Return the URL and the community name in the response
        return Response({"redirect_url": redirect_url, "name": community.name},
                        status=status.HTTP_201_CREATED)
