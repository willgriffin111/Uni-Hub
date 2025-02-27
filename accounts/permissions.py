from rest_framework import permissions

class IsAuthenticatedUser(permissions.BasePermission):
    """
    Grants access only to authenticated users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsCommunityAdmin(permissions.BasePermission):
    pass
    # BLA BLA BLA


class IsEventOrganiser(permissions.BasePermission):
    pass 
    # BLA BLA BLA
