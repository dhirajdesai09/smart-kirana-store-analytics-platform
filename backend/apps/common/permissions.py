from rest_framework import permissions


class IsStoreMember(permissions.BasePermission):
    """Allows access to users attached to the requested store."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        store = getattr(obj, "store", obj)
        return store.memberships.filter(user=request.user, is_active=True).exists()


class IsStoreOwnerOrManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        store = getattr(obj, "store", obj)
        return store.memberships.filter(
            user=request.user,
            is_active=True,
            role__in=["owner", "manager"],
        ).exists()
