# Generated by Django 4.2.7 on 2023-11-04 09:21

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.functions.text


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0011_seed_kpi_aggregations"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="countrykpiaggregation",
            options={
                "ordering": [django.db.models.functions.text.Upper("abstraction_name")],
                "verbose_name": "Country KPI Aggregation Model",
                "verbose_name_plural": "Country KPI Aggregation Models",
            },
        ),
        migrations.AlterModelOptions(
            name="icbkpiaggregation",
            options={
                "ordering": [django.db.models.functions.text.Upper("abstraction_name")],
                "verbose_name": "IntegratedCareBoard KPI Aggregation Model",
                "verbose_name_plural": "IntegratedCareBoard KPI Aggregation Models",
            },
        ),
        migrations.AlterModelOptions(
            name="localhealthboardkpiaggregation",
            options={
                "ordering": [django.db.models.functions.text.Upper("abstraction_name")],
                "verbose_name": "Local Health Board KPI Aggregation Model",
                "verbose_name_plural": "Local Health Board KPI Aggregation Models",
            },
        ),
        migrations.AlterModelOptions(
            name="nationalkpiaggregation",
            options={
                "ordering": [django.db.models.functions.text.Upper("abstraction_name")],
                "verbose_name": "National KPI Aggregation Model",
                "verbose_name_plural": "National KPI Aggregation Models",
            },
        ),
        migrations.AlterModelOptions(
            name="nhsenglandregionkpiaggregation",
            options={
                "ordering": [django.db.models.functions.text.Upper("abstraction_name")],
                "verbose_name": "NHSEnglandRegion KPI Aggregation Model",
                "verbose_name_plural": "NHSEnglandRegion KPI Aggregation Models",
            },
        ),
        migrations.AlterModelOptions(
            name="openukkpiaggregation",
            options={
                "ordering": [django.db.models.functions.text.Upper("abstraction_name")],
                "verbose_name": "OpenUK KPI Aggregation Model",
                "verbose_name_plural": "OpenUK KPI Aggregation Models",
            },
        ),
        migrations.AlterModelOptions(
            name="organisationkpiaggregation",
            options={
                "ordering": [django.db.models.functions.text.Upper("abstraction_name")],
                "verbose_name": "Organisation KPI Aggregation Model",
                "verbose_name_plural": "Organisation KPI Aggregation Models",
            },
        ),
        migrations.AlterModelOptions(
            name="trustkpiaggregation",
            options={
                "ordering": [django.db.models.functions.text.Upper("abstraction_name")],
                "verbose_name": "Trust KPI Aggregation Model",
                "verbose_name_plural": "Trust KPI Aggregation Models",
            },
        ),
        migrations.AlterField(
            model_name="countrykpiaggregation",
            name="abstraction_relation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="epilepsy12.country"
            ),
        ),
        migrations.AlterField(
            model_name="historicalcomorbiditylist",
            name="conceptId",
            field=models.CharField(blank=True, db_index=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="historicalepilepsycause",
            name="conceptId",
            field=models.CharField(blank=True, db_index=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="historicalmedicine",
            name="conceptId",
            field=models.CharField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="icbkpiaggregation",
            name="abstraction_relation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="epilepsy12.integratedcareboard",
            ),
        ),
        migrations.AlterField(
            model_name="localhealthboardkpiaggregation",
            name="abstraction_relation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="epilepsy12.localhealthboard",
            ),
        ),
        migrations.AlterField(
            model_name="medicine",
            name="conceptId",
            field=models.CharField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="nhsenglandregionkpiaggregation",
            name="abstraction_relation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="epilepsy12.nhsenglandregion",
            ),
        ),
        migrations.AlterField(
            model_name="openukkpiaggregation",
            name="abstraction_relation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="epilepsy12.openuknetwork",
            ),
        ),
        migrations.AlterField(
            model_name="organisationkpiaggregation",
            name="abstraction_relation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="epilepsy12.organisation",
            ),
        ),
        migrations.AlterField(
            model_name="trustkpiaggregation",
            name="abstraction_relation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="epilepsy12.trust"
            ),
        ),
    ]
