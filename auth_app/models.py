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
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    img = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username


class Notifications(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.content


class AnonymousUser(models.Model):
    ip_address = models.GenericIPAddressField()
    session_key = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.session_key


class Tag(models.Model):
    hashtag = models.CharField(max_length=255)

    def __str__(self):
        return self.hashtag


class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    anonymous = models.ForeignKey(AnonymousUser, on_delete=models.CASCADE, null=True, blank=True)
    publication = models.ForeignKey('UserPublication', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()

    def __str__(self):
        return self.content


class UserPublication(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey(haka_app.Event, on_delete=models.CASCADE, null=True, blank=True)
    img = models.JSONField(default=[])
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.description

