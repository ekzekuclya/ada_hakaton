from django.contrib import admin
from .models import UserProfile, CustomUser, Notifications, AnonymousUser, UserPublication, Comment, Tag


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user']


@admin.register(CustomUser)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'username']


@admin.register(Notifications)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user']


@admin.register(AnonymousUser)
class AnonymousUser(admin.ModelAdmin):
    list_display = ['ip_address']


@admin.register(UserPublication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ['user_profile']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['hashtag']
