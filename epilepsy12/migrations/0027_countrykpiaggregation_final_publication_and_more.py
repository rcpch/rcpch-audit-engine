# Generated by Django 4.2.4 on 2023-08-17 10:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "epilepsy12",
            "0026_rename_organisation_organisationkpiaggregation_abstraction_relation_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="countrykpiaggregation",
            name="final_publication",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="icbkpiaggregation",
            name="final_publication",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="nhsregionkpiaggregation",
            name="final_publication",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="openukkpiaggregation",
            name="final_publication",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="organisationkpiaggregation",
            name="final_publication",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="trustkpiaggregation",
            name="final_publication",
            field=models.BooleanField(default=False),
        ),
    ]