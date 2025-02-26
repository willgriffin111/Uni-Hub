from rest_framework import permissions

# I HAD TO ADD THIS SO BECAUSE I WAS GETTING AN ERROR - i got it from the lecture example week 17
class IsEditor(permissions.BasePermission):
    """
    Custom permission to only allow editors to edit posts.
    """

    def has_permission(self, request, view):
        # Define your logic for identifying an editor.
        # This could be a check against a group or a specific user attribute.
        return request.user.is_authenticated and request.user.is_editor