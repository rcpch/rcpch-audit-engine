# Generated by Django 4.0.4 on 2022-08-31 16:16

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epilepsy12', '0007_alter_antiepilepsymedicine_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='multiaxialdiagnosis',
            name='seizure_cause_chromosomal_abnormality',
        ),
        migrations.RemoveField(
            model_name='multiaxialdiagnosis',
            name='seizure_cause_gene_abnormality',
        ),
        migrations.RemoveField(
            model_name='multiaxialdiagnosis',
            name='seizure_cause_genetic',
        ),
        migrations.RemoveField(
            model_name='multiaxialdiagnosis',
            name='seizure_cause_genetic_other',
        ),
        migrations.RemoveField(
            model_name='multiaxialdiagnosis',
            name='seizure_cause_immune',
        ),
        migrations.RemoveField(
            model_name='multiaxialdiagnosis',
            name='seizure_cause_immune_antibody',
        ),
        migrations.RemoveField(
            model_name='multiaxialdiagnosis',
            name='seizure_cause_immune_antibody_other',
        ),
        migrations.RemoveField(
            model_name='multiaxialdiagnosis',
            name='seizure_cause_infectious',
        ),
        migrations.RemoveField(
            model_name='multiaxialdiagnosis',
            name='seizure_cause_main',
        ),
        migrations.RemoveField(
            model_name='multiaxialdiagnosis',
            name='seizure_cause_metabolic',
        ),
        migrations.RemoveField(
            model_name='multiaxialdiagnosis',
            name='seizure_cause_metabolic_other',
        ),
        migrations.RemoveField(
            model_name='multiaxialdiagnosis',
            name='seizure_cause_structural',
        ),
        migrations.AddField(
            model_name='multiaxialdiagnosis',
            name='epilepsy_cause_categories',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(help_text='add a category', max_length=500), blank=True, default=list, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='antiepilepsymedicine',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='antiepilepsymedicine',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='case',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='case',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='comorbidity',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='comorbidity',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='epilepsycontext',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='epilepsycontext',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='episode',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='episode',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='initialassessment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='initialassessment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='investigations',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='investigations',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='management',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='management',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='multiaxialdiagnosis',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='multiaxialdiagnosis',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='site',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='site',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='syndrome',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='record created on <function now at 0x1039b4f70>'),
        ),
        migrations.AlterField(
            model_name='syndrome',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='record updated on <function now at 0x1039b4f70>'),
        ),
    ]
