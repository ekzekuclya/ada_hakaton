# Generated by Django 4.2.4 on 2023-10-06 22:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0013_remove_comment_user_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpublication',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
