# Generated by Django 4.2.4 on 2023-10-06 18:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0011_comment_content_comment_user_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpublication',
            name='user_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth_app.userprofile'),
        ),
    ]
