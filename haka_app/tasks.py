from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import Event
from auth_app import models
from django.conf import settings
from django.core.mail import send_mail, EmailMessage


@shared_task
def notify_event_start():
    try:
        now = timezone.now()
        future = now + timedelta(hours=24)
        past = timezone.now() - timedelta(hours=24)
        upcoming_events = Event.objects.filter(start_event_date__lte=future, is_archived=False)
        events_to_archive = Event.objects.filter(start_event_date=past, is_archived=False)
        if events_to_archive:
            for event in events_to_archive:
                event.is_archived = True
                event.hot = False
                for i in event.followers.all():
                    profile = models.UserProfile.objects.get(user=i)
                    profile.future_events.remove(event)
                    profile.visited_events.add(event)
                    event.save()

        if upcoming_events:
            for event in upcoming_events:
                if not event.hot:
                    followers = event.followers.all()
                    for i in followers:
                        subject = f'{i.username} Тебя ждёт ивент!'
                        recipient_list = [i.email]
                        text = f'Привет {i.username} скоро начнётся ивент {event.title}'
                        notification = models.Notifications.objects.create(user=i, content=text)
                        notification.save()
                        event.hot = True
                        event.save()
                        send_email(
                            subject=subject,
                            message=text,
                            recipient_list=recipient_list
                        )
    except Event.DoesNotExist:
        pass


@shared_task
def send_email(subject, message, recipient_list):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipient_list,
        fail_silently=False
    )



