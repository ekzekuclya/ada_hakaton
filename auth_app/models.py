from django.db import models
from django.contrib.auth.models import AbstractUser
from haka_app import models as haka_app


class CustomUser(AbstractUser):
    created_at = models.DateTimeField(auto_now=True)
    is_event_maker = models.BooleanField(default=False)


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    visited_events = models.ManyToManyField(haka_app.Event, related_name='archived_event', blank=True)
    future_events = models.ManyToManyField(haka_app.Event, related_name='subscribed_event', blank=True)
    followers = models.ManyToManyField(CustomUser, 'followers', symmetrical=False)
    following = models.ManyToManyField(CustomUser, 'following', symmetrical=False)


class Notifications(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()


class AnonymousUser(models.Model):
    ip_address = models.GenericIPAddressField()
    session_key = models.CharField(max_length=255, unique=True)