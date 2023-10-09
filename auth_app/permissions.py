from rest_framework import permissions


class UserProfilePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        if view.action in ['retrieve']:
            return True
        if view.action in ['subscribe', 'unsubscribe']:
            return True
        if request.user.is_authenticated:
            if view.action in ['subscribe', 'unsubscribe']:
                return True
        return True


class NotificationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method == 'GET':
                return True
            return False
        return False



