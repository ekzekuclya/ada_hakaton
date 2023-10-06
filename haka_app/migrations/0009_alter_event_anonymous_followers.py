# Generated by Django 4.2.4 on 2023-10-06 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0010_comment_event'),
        ('haka_app', '0008_event_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='anonymous_followers',
            field=models.ManyToManyField(blank=True, related_name='anonymous_follower', to='auth_app.anonymoususer'),
        ),
    ]
