# Generated by Django 4.2.4 on 2023-10-06 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('haka_app', '0009_alter_event_anonymous_followers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='date',
            new_name='end_event_date',
        ),
        migrations.AddField(
            model_name='event',
            name='date_created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='start_event_date',
            field=models.DateField(null=True),
        ),
    ]
