"""
Permissions for Core Application
"""

from rest_framework import permissions


class IsClientOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET" and request.user.role == "CODER":
            return True
        if request.user.role == "CODER":
            return False
        if request.method in ["POST", "PUT", "PATCH"]:
            return request.user.role == "CLIENT"
        return True


class CustomMilestonePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        if request.method in ["POST", "PUT", "PATCH"] and request.user.role == "CODER":
            return True
        return False


class CustomProposalPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        if request.method in ["POST", "PUT", "PATCH"] and request.user.role == "CODER":
            return True
        if request.method in ["PUT", "PATCH"] and request.user.role == "CLIENT":
            return True
        return False


class IsAuthenticatedAndEmailVerified(permissions.BasePermission):
    """
    Allow access only to authenticated and email verified users.
    """

    message = "Please verifiy your email address."

    @staticmethod
    def has_permission(request, view):
        """
        Checking for requested user
        - Should be authenticated
        - Email has to be verified
        """
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_email_verified
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permissiong class to check
    - User is admin or not
    - if not admin then give only readonly access.
    """

    @staticmethod
    def has_permission(request, view):
        if request.method == "POST" and request.user.is_superuser:
            return True
        if request.method == "GET" and (request.user.role in ["CLIENT", "CODER"] or request.user.is_superuser):
            return True
        return False
    

class HasJobInvitationEditPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ("PATCH", "PUT"):
            if request.user.role == "CODER":
                return True
            else: return False
        else:
            if request.user.role == "CODER" and request.method == 'POST':
                return False
        return True

    
class HasTimesheetGetUpdatePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'CLIENT' and request.method in ['GET', 'PUT']:
            return True
        elif request.user.role == 'CODER' and request.method in ['GET', 'POST']:
            return True
        return False
