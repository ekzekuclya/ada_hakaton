# Generated by Django 4.2.4 on 2023-10-05 00:16

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('haka_app', '0005_event_anonymous_followers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='followers',
            field=models.ManyToManyField(null=True, related_name='event_followers', to=settings.AUTH_USER_MODEL),
        ),
    ]
