from rest_framework.permissions import BasePermission


class IsAuthenticatedOrAdmin(BasePermission):
    """
    Allow authenticated users to create, but restrict other actions to admin users.
    """

    def has_permission(self, request, view):
        if view.action == "create" or request.method == "POST":
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class IsProfileOwnerOrAdmin(BasePermission):
    """
    Custom permission to allow only the owner of the profile or an admin user to edit the profile.
    Users are not allowed to delete their profile.
    """

    def has_permission(self, request, view):
        if request.method == "DELETE":
            return (
                request.user and request.user.is_authenticated and request.user.is_staff
            )
        if request.method in ["GET", "HEAD", "OPTIONS", "PUT", "PATCH"]:
            return request.user and request.user.is_authenticated

        return False

    def has_object_permission(self, request, view, obj):
        """
        Custom permission to allow users edit their own profile, or admins can edit profiles.
        """
        if request.method in ["GET", "HEAD", "OPTIONS", "PUT", "PATCH"]:
            return obj.user == request.user or request.user.is_staff
        return False
