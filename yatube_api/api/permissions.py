from rest_framework import permissions


class AuthorOrReading(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.author == request.user:
            return True
