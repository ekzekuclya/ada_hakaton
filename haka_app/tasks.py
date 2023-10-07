from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import Event
from auth_app import models


@shared_task
def notify_event_start():
    try:

        now = timezone.now()
        time_threshold = now + timedelta(hours=24)
        upcoming_events = Event.objects.filter(start_event_date__lte=time_threshold)
        if upcoming_events:
            for event in upcoming_events:
                followers = event.followers.all()
                for i in followers:
                    text = f'{i.username} до ивента {event.title} осталочь 24 ЧАСА!'
                    notification = models.Notifications.objects.create(user=i, content=text)
                    notification.save()
                    event.hot = True
                    event.save()
    except Event.DoesNotExist:
        pass



