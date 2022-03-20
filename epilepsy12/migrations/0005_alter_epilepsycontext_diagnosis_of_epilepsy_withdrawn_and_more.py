# Generated by Django 4.0 on 2022-03-20 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epilepsy12', '0004_remove_epilepsycontext_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='epilepsycontext',
            name='diagnosis_of_epilepsy_withdrawn',
            field=models.CharField(choices=[('Y', 'Yes'), ('N', 'No')], default='N', max_length=2, verbose_name='has the diagnosis of epilepsy been withdrawn?'),
        ),
        migrations.AlterField(
            model_name='epilepsycontext',
            name='is_there_a_family_history_of_epilepsy',
            field=models.CharField(choices=[('Y', 'Yes'), ('N', 'No'), ('U', 'Uncertain')], default='N', max_length=3, verbose_name='is there a family history of epilepsy?'),
        ),
        migrations.AlterField(
            model_name='epilepsycontext',
            name='previous_acute_symptomatic_seizure',
            field=models.CharField(choices=[('Y', 'Yes'), ('N', 'No'), ('U', 'Uncertain')], default='N', max_length=2, verbose_name='has there been a previous acute symptomatic seizure?'),
        ),
        migrations.AlterField(
            model_name='epilepsycontext',
            name='previous_febrile_seizure',
            field=models.CharField(choices=[('Y', 'Yes'), ('N', 'No'), ('U', 'Uncertain')], default='N', max_length=2, verbose_name='has there been a previous febrile seizure?'),
        ),
        migrations.AlterField(
            model_name='epilepsycontext',
            name='previous_neonatal_seizures',
            field=models.CharField(choices=[('Y', 'Yes'), ('N', 'No'), ('U', 'Uncertain')], default='N', max_length=2, verbose_name='were there seizures in the neonatal period?'),
        ),
    ]
