# Generated by Django 4.0.4 on 2022-08-09 20:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epilepsy12', '0026_rename_individualised_care_plan_includes_parental_prolonged_seizure_care_management_individualised_c'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assessment',
            name='has_an_aed_been_given',
        ),
        migrations.RemoveField(
            model_name='assessment',
            name='rescue_medication_prescribed',
        ),
    ]
