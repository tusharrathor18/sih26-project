from rest_framework import permissions

class IsOfficerActive(permissions.BasePermission):
    """
    Allows access only to authenticated officers whose profile and account are active.
    """
    message = "Officer account is inactive or not authorized."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if not request.user.is_active:
            return False
        if hasattr(request.user, 'officer_profile'):
            return request.user.officer_profile.is_active
        return False


class IsAdminOfficer(permissions.BasePermission):
    """
    Allows access only to officers with the 'ADMIN' role.
    """
    message = "Administrative privilege required. Only department admins can perform this action."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.is_active):
            return False
        if hasattr(request.user, 'officer_profile'):
            profile = request.user.officer_profile
            return profile.is_active and (profile.role == 'ADMIN' or request.user.is_superuser)
        return False


class IsInspectorOfficer(permissions.BasePermission):
    """
    Allows access to officers with the 'INSPECTOR' or 'ADMIN' role.
    """
    message = "Inspector authorization required to access this compliance resource."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.is_active):
            return False
        if hasattr(request.user, 'officer_profile'):
            profile = request.user.officer_profile
            return profile.is_active and profile.role in ['INSPECTOR', 'ADMIN']
        return False
