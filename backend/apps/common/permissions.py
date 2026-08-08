from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.users.models import Role


class IsAdmin(BasePermission):
    """Grants access only to users with role=admin (or Django superusers)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.role == Role.ADMIN or user.is_superuser))


class IsOwner(BasePermission):
    """Object-level permission: the object's `user` field must match request.user."""

    owner_field = "user"

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, self.owner_field, None)
        return owner is not None and owner == request.user


class IsOwnerOrAdmin(BasePermission):
    """Owner has full access; admins have read/moderate access to any object."""

    owner_field = "user"

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == Role.ADMIN or user.is_superuser:
            return True
        owner = getattr(obj, self.owner_field, None)
        return owner is not None and owner == user


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        user = request.user
        return bool(user and user.is_authenticated and (user.role == Role.ADMIN or user.is_superuser))
