from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaffOrReadOnly(BasePermission):
    """
    Allow authenticated users to view records,
    and only admin users to update, or delete records.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff


class IsAuthenticatedOrAdmin(BasePermission):
    """
    Allow authenticated users to create, but restrict other actions to admin users.
    """

    def has_permission(self, request, view):
        if request.method == "POST" or view.action == "create":
            return request.user and request.user.is_authenticated
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return request.user and request.user.is_staff


class IsAdminOrReadOnly(BasePermission):
    """
    Allow read-only access to all authenticated users, but restrict write access to admin users.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff
