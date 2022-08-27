# Generated by Django 4.0.4 on 2022-08-27 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epilepsy12', '0064_alter_antiepilepsymedicine_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='investigations',
            name='mri_brain_date',
        ),
        migrations.AddField(
            model_name='investigations',
            name='mri_brain_performed_date',
            field=models.DateField(blank=True, default=None, null=True, verbose_name='MRI brain performed date'),
        ),
        migrations.AddField(
            model_name='investigations',
            name='mri_brain_request_date',
            field=models.DateField(blank=True, default=None, null=True, verbose_name='MRI brain requested date'),
        ),
        migrations.AlterField(
            model_name='antiepilepsymedicine',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='antiepilepsymedicine',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='case',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='case',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='comorbidity',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='comorbidity',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='desscribe',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='desscribe',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='epilepsycontext',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='epilepsycontext',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='initialassessment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='initialassessment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='investigations',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='investigations',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='management',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='management',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='site',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x10e954f70>'),
        ),
        migrations.AlterField(
            model_name='site',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x10e954f70>'),
        ),
    ]
