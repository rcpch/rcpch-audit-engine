# Generated by Django 4.2.9 on 2024-01-11 17:22

from django.db import migrations

import logging

from epilepsy12.common_view_functions import _seed_all_aggregation_models
from epilepsy12.constants import RCPCH_ORGANISATIONS

# Logging setup
logger = logging.getLogger(__name__)


def seed_kpi_aggregations(apps, schema_editor):
    """
    This is a work around as seeding of the database has already happened in migrations 002-0010
    In Migration 0023 the Organisation model has been updated to include email address, and therefore seeding of the
    KPIAggregation models (previously occured in 0011) could not happen until after this step.
    Consequently Migration 0011 has commented out the seed KPIAggregation models call and is reinstated here.
    A check is made in advance of this to make sure this step has not already happened for legacy databases.
    """
    OrganisationKPIAggregation = apps.get_model(
        "epilepsy12", "OrganisationKPIAggregation"
    )
    if OrganisationKPIAggregation.objects.count() == 0:
        logger.debug("Calling seed function of aggregation models")
        _seed_all_aggregation_models()
    else:
        logger.info(
            "The OrganisationKPIAggregation model has already been seeded. Skipping seeding..."
        )


def seed_organisations_with_emails(apps, schema_editor):
    Organisation = apps.get_model("epilepsy12", "Organisation")
    for organisation in RCPCH_ORGANISATIONS:
        if Organisation.objects.filter(
            ods_code=organisation["OrganisationCode"]
        ).exists():
            seeded_equivalent_organisation = Organisation.objects.filter(
                ods_code=organisation["OrganisationCode"]
            ).get()
            seeded_equivalent_organisation.email = organisation["Email"]
            seeded_equivalent_organisation.save(update_fields=["email"])
        else:
            logger.warn(
                f"{organisation['OrganisationCode']} ({organisation['OrganisationName']}) does not exist in the database."
            )


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0023_historicalorganisation_email_organisation_email"),
    ]

    operations = [
        migrations.RunPython(seed_kpi_aggregations),
        migrations.RunPython(seed_organisations_with_emails),
    ]
