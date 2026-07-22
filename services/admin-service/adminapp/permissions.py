from rest_framework.permissions import BasePermission


class IsRole(BasePermission):
    """Usage: permission_classes = [IsRole('org_admin', 'instructor')]"""

    def __init__(self, *roles):
        self.roles = roles

    def __call__(self):
        return self

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and getattr(user, "is_authenticated", False) and user.role in self.roles)


class IsAuthenticatedStateless(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and getattr(user, "is_authenticated", False))


class IsTenantScoped(BasePermission):
    """Platform admins cross tenant boundaries; everyone else must belong
    to an organization. Combine with IsRole/IsAuthenticatedStateless."""

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False
        if user.role == "platform_admin":
            return True
        return bool(user.organization_id)
