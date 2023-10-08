from rest_framework import permissions


class DefaultPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        if request.user.is_authenticated:
            if request.method in ['POST', 'PUT', 'PATCH']:
                return True
        if view.action == 'follow':
            return True


