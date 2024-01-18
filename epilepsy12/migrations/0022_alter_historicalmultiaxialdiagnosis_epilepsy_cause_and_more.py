# Generated by Django 4.2.9 on 2024-01-10 15:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0021_alter_episode_seizure_onset_date_confidence_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalmultiaxialdiagnosis",
            name="epilepsy_cause",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                default=None,
                help_text={
                    "label": "Please select the main identified cause of the epilepsy. If the cause is not in this list, please email the Epilepsy12 team",
                    "reference": "Please select the main identified cause of the epilepsy. If the cause is not in this list, please email the Epilepsy12 team",
                },
                max_length=250,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="epilepsy12.epilepsycause",
            ),
        ),
        migrations.AlterField(
            model_name="multiaxialdiagnosis",
            name="epilepsy_cause",
            field=models.ForeignKey(
                blank=True,
                default=None,
                help_text={
                    "label": "Please select the main identified cause of the epilepsy. If the cause is not in this list, please email the Epilepsy12 team",
                    "reference": "Please select the main identified cause of the epilepsy. If the cause is not in this list, please email the Epilepsy12 team",
                },
                max_length=250,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="epilepsy12.epilepsycause",
            ),
        ),
    ]