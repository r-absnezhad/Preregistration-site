from rest_framework.permissions import BasePermission

class IsAuthenticatedOrAdmin(BasePermission):
    """
    Allow authenticated users to create records,
    and only admin users to view, update, or delete records.
    """

    def has_permission(self, request, view):
        if view.action == "create" and request.user.is_authenticated:
            return True
        return request.user.is_staff
