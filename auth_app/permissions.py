# from rest_framework import permissions
#
#
# class UserProfilePermission(permissions.BasePermission):
#     def has_permission(self, request, view):
#         if view.action == 'retrieve':
#             return True
#         return False
#
#     def has_object_permission(self, request, view, obj):
#         return obj.user == request.user or request.user.is_staff
from rest_framework import permissions


class UserProfilePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        if view.action in ['retrieve']:
            return True
        if view.action in ['subscribe', 'unsubscribe']:
            return True
        # if request.user.is_authenticated:
        #
        #     if view.action in ['subscribe', 'unsubscribe']:
        #         return True
        return False


class NotificationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method == 'GET':
                return True
            return False
        return False
