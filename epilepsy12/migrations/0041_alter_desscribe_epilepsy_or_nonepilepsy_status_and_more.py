# Generated by Django 4.0.4 on 2022-08-16 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epilepsy12', '0040_alter_antiepilepsymedicine_management'),
    ]

    operations = [
        migrations.AlterField(
            model_name='desscribe',
            name='epilepsy_or_nonepilepsy_status',
            field=models.CharField(blank=True, choices=[('E', 'Epilepsy'), ('NE', 'Non-epilepsy'), ('U', 'Uncertain')], default=None, max_length=3, null=True, verbose_name='Is a diagnosis of epilepsy definite, or uncertain.'),
        ),
        migrations.AlterField(
            model_name='desscribe',
            name='epileptic_seizure_onset_type',
            field=models.CharField(choices=[('FO', 'Focal onset'), ('GO', 'Generalised onset'), ('UO', 'Unknown onset'), ('UC', 'Unclassified')], default=None, max_length=3, null=True, verbose_name='If epileptic, what is the seizure type (s)?'),
        ),
    ]
