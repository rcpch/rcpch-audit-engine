# Generated by Django 4.0.4 on 2022-07-28 22:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epilepsy12', '0016_initialassessment_episode_definition'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='epilepsycontext',
            name='date_of_first_epileptic_seizure',
        ),
    ]
