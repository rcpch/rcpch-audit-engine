# Generated by Django 4.2 on 2023-04-12 14:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0084_create_foreign_keys_for_existing_meds"),
    ]

    operations = [
        migrations.AlterField(
            model_name="antiepilepsymedicine",
            name="medicine_entity",
            field=models.ForeignKey(
                default=None,
                null=True,
                help_text={
                    "label": "Medicine Name",
                    "reference": "Please enter the medicine.",
                },
                on_delete=django.db.models.deletion.PROTECT,
                to="epilepsy12.medicineentity",
            ),
        ),
    ]