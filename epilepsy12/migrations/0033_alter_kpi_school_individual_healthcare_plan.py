# Generated by Django 5.1 on 2024-10-08 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("epilepsy12", "0032_organisationalauditsubmissionperiod_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="kpi",
            name="school_individual_healthcare_plan",
            field=models.IntegerField(
                default=None,
                help_text={
                    "label": "10. School Individual Health Care Plan",
                    "reference": "Percentage of children and young people with epilepsy aged 4 years and above with evidence of a school individual healthcare plan by 1 year after first paediatric assessment.",
                },
                null=True,
            ),
        ),
    ]
