from django.db import models
from auth_app import models as md


class Event(models.Model):
    user = models.ForeignKey('auth_app.CustomUser', on_delete=models.CASCADE)
    PRIORITY = (
        ('city_event', 'Масштабный ивент'),
        ('weeks_event', 'Ивенты от юрлиц'),
        ('users_event', 'Ивенты от пользователей')
    )
    priority = models.CharField(choices=PRIORITY, max_length=255, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_created = models.DateField(null=True, auto_now_add=True)
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
    anonymous_followers = models.ManyToManyField('auth_app.AnonymousUser', related_name='anonymous_follower', blank=True)
    tags = models.ManyToManyField('auth_app.Tag', blank=True)
    img = models.JSONField(default=[], blank=True)
    start_event_date = models.DateField(null=True, blank=True)
    hot = models.BooleanField(default=False)
    end_event_date = models.DateField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    limit_of_followers = models.PositiveIntegerField(null=True, blank=True)

    def count_followers(self):
        return self.followers.count()

    def __str__(self):
        return self.title

