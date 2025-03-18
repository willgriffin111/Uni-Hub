from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Community
from django.contrib.auth import get_user_model
from django.http import JsonResponse

class CommunityViewAPI(APIView):
    def get(self, request):
        # Create a dummy user to associate with the community
        User = get_user_model()
        dummy_user = User.objects.first()  # Get the first user, assuming at least one user exists
        
        if not dummy_user:
            return JsonResponse({"error": "No user found to create community."}, status=400)

        # Create a dummy community
        community = Community.objects.create(
            name="Dummy Community",
            description="This is a dummy community created for testing.",
            created_by=dummy_user,
            contact_email="dummy@community.com"
        )

        # Add the dummy user to the members list
        community.members.add(dummy_user)

        # Return a success response with the community details
        return JsonResponse({
            "name": community.name,
            "description": community.description,
            "created_by": community.created_by.username,
            "contact_email": community.contact_email,
            "created_at": community.created_at,
            "members": [user.username for user in community.members.all()],
        })
