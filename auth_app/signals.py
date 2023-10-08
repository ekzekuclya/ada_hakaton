from django.db.models.signals import pre_save, post_save
from .models import CustomUser, UserProfile, Notifications, UserPublication, Comment, AnonymousUser
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from random import choice, randint
from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer
#
# channel_layer = get_channel_layer()


image_list = ["https://i.pinimg.com/236x/51/91/dc/5191dc77fb76fa9ef4a11eef260b101f.jpg",
              "https://i.pinimg.com/236x/21/fc/fd/21fcfd108a79026900ff6bd8a0563095.jpg",
              "https://i.pinimg.com/236x/c8/73/34/c87334fe49476009f5d367d145c80751.jpg",
              "https://i.pinimg.com/236x/e8/32/12/e8321254fcfa739945ff2be6ae6cf959.jpg",
              "https://i.pinimg.com/236x/a2/d0/11/a2d011fd77bd1c37b08cf6ca0ff42e37.jpg",
              "https://i.pinimg.com/236x/6a/96/dc/6a96dc859d024bb1e7162aa7b8c355a0.jpg",
              "https://i.pinimg.com/236x/6f/75/dd/6f75dd3224eb393b8db83eabcba64595.jpg",
              "https://i.pinimg.com/236x/fa/24/9c/fa249c8561a4c4c912ae4214983ca726.jpg",
              "https://i.pinimg.com/236x/e3/cb/58/e3cb58ae530636c8ea84c10d50308687.jpg"
              ]


@receiver(post_save, sender=CustomUser)
def create_userprofile(sender, instance, created, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance, img=[choice(image_list) + ", " for i in range(randint(1, 3))]) ## GENERATOR
        text = f'С регистрацией {instance.username}!'
        notification = Notifications.objects.create(user=instance, content=text)
        notification.save()
        userprofile.save()


# @receiver(post_save, sender=AnonymousUser)
# def create_userprofile(sender, instance, created, **kwargs):
#     if created:
#         userprofile = UserProfile.objects.create(user=instance, img=[choice(image_list) + ", " for i in range(randint(1, 3))]) ## GENERATOR
#         text = f'С регистрацией {instance.username}!'
#         notification = Notifications.objects.create(user=instance, content=text)
#         notification.save()
#         userprofile.save()


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


@receiver(post_save, sender=UserPublication)
def notification_to_followers(sender, instance, created, **kwargs):
    print(instance.user_profile)
    if created:
        user = instance.user_profile.user
        text = f'Ожидаемый вами ивент опубликовал пост! {instance.description}'
        notification = Notifications.objects.create(user=user, content=text)
        notification.save()


# @receiver(post_save, sender=Notifications)
# def send_notification(sender, instance, created, **kwargs):
#     if created:
#         group_name = f"user_{instance.user.id}"  # Создайте группу веб-сокета для каждого пользователя
#         async_to_sync(channel_layer.group_send)(
#             group_name,
#             {
#                 "type": "notification.message",
#                 "message": instance.content,  # Ваш текст уведомления
#             },
#         )




