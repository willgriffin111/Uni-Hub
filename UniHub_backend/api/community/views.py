from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CommunitySerializer, CommunityEventSerializer, CommunityEventAttendanceSerializer, CommunityRoleUpdateSerializer
from rest_framework import generics, permissions, status
from django.http import JsonResponse
import os
from django.core.files import File
from .models import Community, CommunityRole, CommunityEvent, CommunityEventAttendance, CommunityBlock
from api.accounts.models import CustomUser
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from django.db.models import Q
import requests
from datetime import datetime


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
        role = CommunityRole.objects.filter(
            user=request.user,
            community=event.community
        ).first()
        if not role or not role.has_permission("member"):
            return JsonResponse(
                {"detail": "You must be a member to attend."},
                status=403
            )

        existing = CommunityEventAttendance.objects.filter(
            user=request.user,
            event=event
        ).first()

        if existing:
            new_status = "no" if existing.status == "yes" else "yes"
        else:
            new_status = "yes"

        attendance, _ = CommunityEventAttendance.objects.update_or_create(
            user=request.user,
            event=event,
            defaults={"status": new_status}
        )

        if new_status == "yes":
            event_dt = datetime.combine(event.event_date, event.event_time)
            payload = {
                "email":             request.user.email,
                "event_title":       event.title,
                "event_description": event.description,
                "event_date":        event_dt.strftime("%B %d, %Y"),
                "event_time":        event_dt.strftime("%I:%M %p"),
                "event_location":    event.location or "To be announced",
            }
            try:
                resp = requests.post(
                    "http://notification:8001/send-event-confirmation",
                    json=payload,
                    timeout=5
                )
                if resp.status_code != 200:
                    print(
                        f"Notif svc error {resp.status_code}: {resp.text}"
                    )
            except Exception as e:
                print(f"Error calling notification svc: {e}")

        return JsonResponse(
            {
                "detail": f"Attendance marked as '{new_status}'",
                "status":  new_status
            },
            status=200
        )


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
                Q(name__icontains=query) | Q(description__icontains=query) | Q(tags__icontains=query)
            )
        else:
            communities = Community.objects.none()
        serializer = CommunitySerializer(communities, many=True, context={'request': request})
        return Response(serializer.data)
    
# ------------------------ROLES------------------------

ROLE_HIERARCHY = {
    'member': 1,
    'event_leader': 2,
    'community_leader': 3,
    'admin': 4
}

class PermoteMemberAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Promote a user to a higher role in the community.
        wont let users permote themselves or demote users
        also checks role permissions to ensure user is allowed to permote others
        this is kinda messy i know but it should cover all possible issues so :|
        """
        community_id = request.data.get('community_id')
        permote_user_id = request.data.get('permote_user_id')
        permote_role = request.data.get('permote_role')
        user = request.user

        community = get_object_or_404(Community, id=community_id)
        permote_user = get_object_or_404(CustomUser, id=permote_user_id)
        if user == permote_user:
            return Response({"detail": "You cannot permote yourself."}, status=status.HTTP_400_BAD)
        
        user_role = get_object_or_404(CommunityRole,user=user, community=community)
        permote_user_role = get_object_or_404(CommunityRole,user=permote_user, community=community)
        
        user_role_level = ROLE_HIERARCHY.get(user_role.role, 0)
        permote_role_level = ROLE_HIERARCHY.get(permote_role, 0)
        if user_role_level >= 3 and user_role_level >= permote_role_level:
            permote_user_role_level = ROLE_HIERARCHY.get(permote_user_role.role, 0)
            if permote_user_role_level >= permote_role_level:
                return Response({"detail": "You cannot permote this user."}, status=status.HTTP_400)
            
            serializer = CommunityRoleUpdateSerializer(instance=permote_user_role, data={'role': permote_role}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"detail": f"{permote_user.username} promoted to {permote_role}."}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response({"detail": "You dont have permission to permote to this level."}, status=status.HTTP_400_BAD)
        
        
class DemoteMemberAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Allows an admin or community creator to demote another user within the community.
        You cannot demote yourself.
        You can only demote users with a lower role.
        """
        community_id = request.data.get('community_id')
        demote_user_id = request.data.get('demote_user_id')
        demote_role = request.data.get('demote_role') 
        user = request.user
        

        community = get_object_or_404(Community, id=community_id)
        demote_user = get_object_or_404(CustomUser, id=demote_user_id)

        if user == demote_user:
            return Response({"detail": "You cannot demote yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Check that both the requester and target have roles in the community
        user_role = get_object_or_404(CommunityRole, user=user, community=community)
        demote_user_role = get_object_or_404(CommunityRole, user=demote_user, community=community)

        user_role_level = ROLE_HIERARCHY.get(user_role.role, 0)
        demote_user_role_level = ROLE_HIERARCHY.get(demote_user_role.role, 0)
        new_role_level = ROLE_HIERARCHY.get(demote_role, 0)

        # Can only demote if the acting user is admin or creator
        is_admin = user_role.role == 'admin'
        is_creator = community.created_by == user

        if not (is_admin or is_creator):
            return Response({"detail": "You don't have permission to demote users."}, status=status.HTTP_403_FORBIDDEN)

        if new_role_level >= demote_user_role_level:
            return Response({"detail": "You can only demote users to a *lower* role than they currently have."}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent demoting someone with equal or higher role unless admin
        if demote_user_role_level >= user_role_level and not is_creator:
            return Response({"detail": "You can't demote a user with an equal or higher role."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommunityRoleUpdateSerializer(instance=demote_user_role, data={'role': demote_role}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": f"{demote_user.username} was demoted to {demote_role}."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class BlockMemberAPI(APIView):
    """
    Allows an admin or community leader to block a user from a community.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        community = get_object_or_404(Community, id=request.data.get('community_id'))
        block_user = get_object_or_404(CustomUser, id=request.data.get('user_id'))
        reason = request.data.get('reason')
        user = request.user

        if user == block_user:
            return Response({"detail": "You cannot block yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Check that both the requester and target have roles in the community
        user_role = get_object_or_404(CommunityRole, user=user, community=community)
        block_user_role = get_object_or_404(CommunityRole, user=block_user, community=community)

        user_role_level = ROLE_HIERARCHY.get(user_role.role, 0)
        if user_role_level < 3:
            return Response({"detail": "You must be a community leader or higher to block users."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        # Create a new block entry
        CommunityBlock.objects.create(user=block_user, community=community, reason=reason)
        
        return Response({"detail": f"{block_user.username} was blocked."}, status=status.HTTP_200_OK)
    
    
class UnBlockMemberAPI(APIView):
    """
    Allows an admin or community leader to unblock a user from a community.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        community = get_object_or_404(Community, id=request.data.get('community_id'))
        unblock_user = get_object_or_404(CustomUser, id=request.data.get('user_id'))
        user = request.user
        
        if user == unblock_user:
            return Response({"detail": "You cannot unblock yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Check that both the requester and target have roles in the community
        user_role = get_object_or_404(CommunityRole, user=user, community=community)
        block_user_role = get_object_or_404(CommunityRole, user=unblock_user, community=community)

        user_role_level = ROLE_HIERARCHY.get(user_role.role, 0)
        if user_role_level < 3:
            return Response({"detail": "You must be a community leader or higher to unblock users."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete the block entry
        CommunityBlock.objects.filter(user=unblock_user, community=community).delete()
        
        # Optionally send a notification or handle additional logic
        return Response({"detail": f"{unblock_user.username} was unblocked."}, status=status.HTTP_200_OK)