# Generated by Django 4.2.4 on 2023-10-07 00:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0015_remove_comment_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='anonymous',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth_app.anonymoususer'),
            preserve_default=False,
        ),
    ]
