# Generated by Django 4.2.4 on 2023-10-06 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('haka_app', '0010_rename_date_event_end_event_date_event_date_created_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='limit_of_followers',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='priority',
            field=models.CharField(choices=[('city_event', 'Масштабный ивент'), ('weeks_event', 'Ивенты от юрлиц'), ('users_event', 'Ивенты от пользователей')], default=1, max_length=255),
            preserve_default=False,
        ),
    ]