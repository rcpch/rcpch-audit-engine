# Generated by Django 4.1.5 on 2023-01-22 15:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epilepsy12', '0048_visitactivity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visitactivity',
            name='login_datetime',
        ),
        migrations.RemoveField(
            model_name='visitactivity',
            name='login_failed_datetime',
        ),
        migrations.RemoveField(
            model_name='visitactivity',
            name='logout_datetime',
        ),
        migrations.AddField(
            model_name='visitactivity',
            name='activity',
            field=models.PositiveSmallIntegerField(choices=[(1, 'SUCCESSFUL_LOGIN'), (2, 'UNSUCCESSFUL_LOGIN'), (3, 'LOGOUT')], default=1),
        ),
        migrations.AddField(
            model_name='visitactivity',
            name='activity_datetime',
            field=models.DateTimeField(auto_created=True, default=datetime.datetime(2023, 1, 22, 15, 31, 49, 415754, tzinfo=datetime.timezone.utc)),
        ),
    ]
