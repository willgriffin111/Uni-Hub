from rest_framework.views import APIView
from rest_framework.response import Response
from api.community.models import Community, CommunityRole
from .serializers import CommunitySerializer, CommunityEventSerializer, CommunityEventAttendanceSerializer
from rest_framework import generics, permissions, status
from django.http import JsonResponse
import os
from django.core.files import File
from .models import Community, CommunityRole, CommunityEvent, CommunityEventAttendance
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from django.db.models import Q


class CommunityEditAPI(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        community = get_object_or_404(Community, id=request.data.get('community_id'))
        user_role = CommunityRole.objects.filter(user=request.user, community=community).first()

        if not user_role or not user_role.has_permission('community_leader'):
            return Response({"detail": "You do not have permission to edit this community."}, status=status.HTTP_403_FORBIDDEN)

        # Check if a new image is provided in the request
        new_image = request.FILES.get('community_image')

        # Delete the old image if a new image is provided and it's not the default
        if new_image and community.community_image.name != 'community/images/default.png':
            # Delete the old image from storage
            old_image_path = community.community_image.path
            if default_storage.exists(old_image_path):
                default_storage.delete(old_image_path)
                
        # Use serializer to update the community details
        serializer = CommunitySerializer(community, data=request.data, partial=True)  # partial=True allows partial updates
        if serializer.is_valid():
            updated_community = serializer.save()  # Save the updated community

            # Return the redirect URL in the response
            redirect_url = reverse('community_page', args=[updated_community.name])

            return Response({
                'message': 'Community updated successfully',
                'redirect_url': redirect_url  # Send the redirect URL
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class CommunityJoinAPI(APIView):
    """
    API endpoint for users to join or leave a community.
    Expects a POST request with community_id.
    If the user is already a member, they will leave the community.
    """
    
    def post(self, request, *args, **kwargs):
        community_id = request.data.get('community_id')
        
        # Get the community or return an error if it doesn't exist
        community = get_object_or_404(Community, id=community_id)
        
        # Get the user who is making the request
        user = request.user
        
        # Check if the user is already a member of the community
        existing_role = CommunityRole.objects.filter(user=user, community=community).first()

        if existing_role:
            # User is a member, so remove them from the community
            community.members.remove(user)  # Remove from the many-to-many field
            existing_role.delete()  # Delete the role entry
            return Response({"detail": "You have left the community."}, status=status.HTTP_200_OK)
        
        # User is not a member, so add them to the community
        community.members.add(user)
        
        # Assign the default 'member' role to the user
        CommunityRole.objects.create(user=user, community=community, role='member')
        return Response({"detail": "Successfully joined the community!"}, status=status.HTTP_200_OK)
    
    

class CreateCommunityView(generics.CreateAPIView):
    """
    POST /api/community/community/ -> Creates a new community.
    The creator is set as the admin and automatically added as a member.
    """
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Validate data using the serializer.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Save the community with created_by as the current user.
        community = serializer.save(created_by=request.user)
        # Add creator as a member and assign the admin role.
        community.members.add(request.user)
        CommunityRole.objects.create(user=request.user, community=community, role='community_leader')
        # Construct the redirect URL (adjust as needed: here we use community name)
        redirect_url = f"/community/{community.name}/"
        return Response({"redirect_url": redirect_url}, status=status.HTTP_201_CREATED)

class DeleteCommunityView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)
        user_role = CommunityRole.objects.filter(user=request.user, community=community).first()

        if not user_role or not user_role.has_permission('community_leader'):
            return Response({"detail": "You do not have permission to delete this community."}, status=status.HTTP_403_FORBIDDEN)

        community.delete()
        return Response({"detail": "Community deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# ------------------------EVENTS------------------------

class CommunityEventCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)
        user_role = CommunityRole.objects.filter(user=request.user, community=community).first()

        if not user_role or not user_role.has_permission('event_leader'):
            return Response({"detail": "You do not have permission to create events."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommunityEventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(community=community)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommunityEventListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)
        events = community.events.all().order_by('event_date', 'event_time')
        serializer = CommunityEventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)



class CommunityEventDetailAPI(APIView):
    def get(self, request, event_id):
        event = get_object_or_404(CommunityEvent, id=event_id)
        serializer = CommunityEventSerializer(event)
        return Response(serializer.data)


class MarkAttendanceAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        event = get_object_or_404(CommunityEvent, id=event_id)
        community = event.community
        user_role = CommunityRole.objects.filter(user=request.user, community=community).first()

        if not user_role or not user_role.has_permission('member'):
            return Response({"detail": "You must be apart of this community to attend."}, status=status.HTTP_403_FORBIDDEN)
        
        status_choice = request.data.get('status')

        if status_choice not in ['yes', 'no']:
            return Response({"detail": "Invalid status. Use 'yes' or 'no'."},
                            status=status.HTTP_400_BAD_REQUEST)

        attendance, created = CommunityEventAttendance.objects.update_or_create(
            user=request.user,
            event=event,
            defaults={'status': status_choice}
        )

        return Response({"detail": f"Marked as {status_choice} for event '{event.title}'"},
                        status=status.HTTP_200_OK)


class AttendanceListAPI(APIView):
    def get(self, request, event_id):
        event = get_object_or_404(CommunityEvent, id=event_id)
        attendances = event.attendances.all()
        serializer = CommunityEventAttendanceSerializer(attendances, many=True)
        return Response(serializer.data)
    
    
class CommunityEventDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, event_id):
        event = get_object_or_404(CommunityEvent, id=event_id)
        community = event.community
        user_role = CommunityRole.objects.filter(user=request.user, community=community).first()

        if not user_role or not user_role.has_permission('event_leader'):
            return Response({"detail": "You do not have permission to delete events."}, status=status.HTTP_403_FORBIDDEN)
        
        event.delete()
        return Response({"detail": "Event deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class CommunityEventEditAPI(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, event_id):
        event = get_object_or_404(CommunityEvent, id=event_id)
        community = event.community
        user_role = CommunityRole.objects.filter(user=request.user, community=community).first()

        if not user_role or not user_role.has_permission('event_leader'):
            return Response({"detail": "You do not have permission to edit events."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommunityEventSerializer(event, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
# ------------------------SEARCH------------------------
    
class CommunitySearchAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('query', '').strip()
        if query:
            communities = Community.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        else:
            communities = Community.objects.none()
        serializer = CommunitySerializer(communities, many=True, context={'request': request})
        return Response(serializer.data)