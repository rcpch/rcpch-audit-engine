# Generated by Django 4.2 on 2023-04-13 10:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0082_alter_kpi_assessment_of_mental_health_issues_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="kpi",
            name="service_contact_details",
            field=models.IntegerField(
                default=None,
                help_text={
                    "label": "9e. Service contact details",
                    "reference": "Percentage of children and young people with epilepsy with evidence of being given service contact details.",
                },
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="kpi",
            name="sudep",
            field=models.IntegerField(
                default=None,
                help_text={
                    "label": "9f. Sudden unexplained death in epilepsy",
                    "reference": "Percentage of children and young people with epilepsy with evidence of discussion regarding SUDEP and evidence of a prolonged seizures care plan.",
                },
                null=True,
            ),
        ),
    ]