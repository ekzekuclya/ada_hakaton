# Generated by Django 4.2.4 on 2023-10-07 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0015_remove_comment_event'),
        ('haka_app', '0011_event_limit_of_followers_event_priority'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_event_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='img',
            field=models.JSONField(blank=True, default=[]),
        ),
        migrations.AlterField(
            model_name='event',
            name='limit_of_followers',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='priority',
            field=models.CharField(blank=True, choices=[('city_event', 'Масштабный ивент'), ('weeks_event', 'Ивенты от юрлиц'), ('users_event', 'Ивенты от пользователей')], max_length=255),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_event_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='tags',
            field=models.ManyToManyField(blank=True, to='auth_app.tag'),
        ),
    ]
