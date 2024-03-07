from rest_framework import permissions


class IsClientOrCoderPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ["POST", "PUT", "GET", "PATCH"]:
            return (
                request.user.role == "CLIENT" or request.user.role == "CODER"
            )  # noqa : E501
        return True


class IsClientOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == "CODER":
            return False
        if request.method in ["POST", "PUT", "PATCH"]:
            return request.user.role == "CLIENT"
        return True


class IsEmailVerified(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        if not is_authenticated:
            return is_authenticated
        if not request.user.is_email_verified:
            return False
        return True
    

class IsCoder(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == "CODER":
            return True
        return False


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == "SUPER-ADMIN":
            return True
        return False


class IsClientOrCoder(permissions.BasePermission):
    """
    Custom permission to allow access only to clients or coders.
    """
    def has_permission(self, request, view):
        return request.user.role in ['CLIENT', 'CODER']
