from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Event
from auth_app import models as auth_md
from django.db.models.signals import m2m_changed


@receiver(post_save, sender=Event)
def notification_to_followers(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        followers = instance.user.followers.all()
        for i in followers:
            text = f'{user.username} создал новое событие'
            notification = auth_md.Notifications.objects.create(user=i.user, content=text)
            notification.save()


@receiver(m2m_changed, sender=Event.followers.through)
def notification_to_event_owner(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        event_owner = instance.user
        new_follower = auth_md.CustomUser.objects.filter(id__in=pk_set).first()
        if new_follower:
            text = f'{new_follower.username} подписался на ваше событие "{instance.title}"'
            notification = auth_md.Notifications.objects.create(user=event_owner, content=text)
            notification.save()




