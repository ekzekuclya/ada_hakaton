from django.db.models.signals import pre_save, post_save
from .models import CustomUser, UserProfile, Notifications
from django.db.models.signals import m2m_changed
from django.dispatch import receiver


@receiver(post_save, sender=CustomUser)
def create_userprofile(sender, instance, created, **kwargs):
    userprofile, created = UserProfile.objects.get_or_create(user=instance)
    if created:
        text = f'С регистрацией {instance.username}!'
        notification = Notifications.objects.create(user=instance, content=text)
        notification.save()
    userprofile.save()


@receiver(m2m_changed, sender=UserProfile.followers.through)
def create_notification(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        if pk_set:
            followed_user = instance.user
            following_user = CustomUser.objects.filter(id__in=pk_set).first()
            notification, created = Notifications.objects.get_or_create(user=followed_user,
                                                                        content=f"{following_user.username} "
                                                                                f""f"is now following you.")
            if created:
                notification.save()




