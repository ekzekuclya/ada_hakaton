from django.db import models
from auth_app import models as md



class Event(models.Model):
    user = models.ForeignKey('auth_app.CustomUser', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(null=True)
    location = models.JSONField(default={})
    display_to_all = models.BooleanField(default=True)
    display_to_followers = models.BooleanField(default=False)
    CAN_SUBSCRIBE = (
        ('all', 'Могут подписаться все'),
        ('authenticated_users', 'Авторизованные пользователи'),
        ('friends', 'Только друзья')
    )
    is_free = models.BooleanField(default=True)
    can_subscribe = models.CharField(choices=CAN_SUBSCRIBE, max_length=255, default='all')
    followers = models.ManyToManyField('auth_app.CustomUser', related_name='event_followers', null=True, blank=True)
    anonymous_followers = models.ManyToManyField('auth_app.AnonymousUser', related_name='anonymous_follower', null=True, blank=True)
    tags = models.ManyToManyField('auth_app.Tag')

