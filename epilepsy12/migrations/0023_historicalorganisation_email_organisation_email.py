# Generated by Django 4.2.9 on 2024-01-11 11:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "epilepsy12",
            "0022_alter_historicalmultiaxialdiagnosis_epilepsy_cause_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalorganisation",
            name="email",
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="email",
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
    ]
