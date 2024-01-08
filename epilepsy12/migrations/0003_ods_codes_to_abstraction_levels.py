from datetime import date
import logging

from django.db import migrations
from ..constants import (
    INTEGRATED_CARE_BOARDS,
    NHS_ENGLAND_REGIONS,
    OPEN_UK_NETWORKS,
    LOCAL_HEALTH_BOARDS,
)

# Logging setup
logger = logging.getLogger(__name__)


def ods_codes_to_abstraction_levels(apps, schema_editor):
    """
    Updates all the abstraction level models with ODS codes
    """
    IntegratedCareBoard = apps.get_model("epilepsy12", "IntegratedCareBoard")
    NHSEnglandRegion = apps.get_model("epilepsy12", "NHSEnglandRegion")
    OPENUKNetwork = apps.get_model("epilepsy12", "OPENUKNetwork")
    LocalHealthBoard = apps.get_model("epilepsy12", "LocalHealthBoard")

    logger.debug(
        "\033[38;2;17;167;142m",
        "Updating Integrated Care Boards with ODS codes",
        "\033[38;2;17;167;142m",
    )

    for icb in INTEGRATED_CARE_BOARDS:
        # iterates through all 42 ICBs and updates model with ODS code
        if IntegratedCareBoard.objects.filter(
            boundary_identifier=icb["gss_code"]
        ).exists():
            # should already exist in the database
            IntegratedCareBoard.objects.filter(
                boundary_identifier=icb["gss_code"]
            ).update(ods_code=icb["ods_code"], publication_date=date(2023, 3, 15))
            logger.debug(f"Updated {icb['name']} to include ODS code")
        else:
            raise Exception(
                f"Seeding error. {icb['gss_code']}/{icb['name']} not found in the database to seed."
            )

    logger.debug(
        "\033[38;2;17;167;142m",
        "Updating NHS England Regions with NHS England region codes",
        "\033[38;2;17;167;142m",
    )

    for nhs_england_region in NHS_ENGLAND_REGIONS:
        # iterates through all 42 ICBs and updates model with ODS code
        if NHSEnglandRegion.objects.filter(
            boundary_identifier=nhs_england_region["NHS_ENGLAND_REGION_ONS_CODE"]
        ).exists():
            # should already exist in the database
            nhs_england_region_object = NHSEnglandRegion.objects.filter(
                boundary_identifier=nhs_england_region["NHS_ENGLAND_REGION_ONS_CODE"]
            ).get()
            nhs_england_region_object.region_code = nhs_england_region[
                "NHS_ENGLAND_REGION_CODE"
            ]
            nhs_england_region_object.publication_date = date(2022, 7, 30)
            nhs_england_region_object.save()
            logger.debug(
                f"Updated {nhs_england_region['NHS_ENGLAND_REGION_NAME']} to include ODS code"
            )
        else:
            raise Exception("Seeding error. No NHS England region entity to seed.")

    logger.debug(
        "\033[38;2;17;167;142m",
        "Updating Local Health Boards with ODS codes.",
        "\033[38;2;17;167;142m",
    )

    for local_health_board in LOCAL_HEALTH_BOARDS:
        # iterates through all 42 ICBs and updates model with ODS code
        if LocalHealthBoard.objects.filter(
            boundary_identifier=local_health_board["gss_code"]
        ).exists():
            # should already exist in the database
            LocalHealthBoard.objects.filter(
                boundary_identifier=local_health_board["gss_code"]
            ).update(
                ods_code=local_health_board["ods_code"],
                publication_date=date(2022, 4, 14),
            )
            logger.debug(f"Updated {local_health_board['health_board']} to include ODS code")
        else:
            raise Exception("Seeding error. No Local Health Board entity to seed.")

    logger.debug(
        "\033[38;2;17;167;142m",
        "Creating OPEN UK Networks...",
        "\033[38;2;17;167;142m",
    )

    for open_uk_network in OPEN_UK_NETWORKS:
        # iterates through all 42 ICBs and populates table
        if OPENUKNetwork.objects.all().count() == 30:
            # should NOT already exist in the database
            logger.debug(
                f"OPEN UK Networks {open_uk_network['name']} have already been added to the database."
            )
            pass
        else:
            OPENUKNetwork.objects.create(
                name=open_uk_network["OPEN_UK_Network_Name"],
                boundary_identifier=open_uk_network["OPEN_UK_Network_Code"],
                country=open_uk_network["country"],
                publication_date=date(2022, 12, 8),
            ).save()
            logger.debug(f"Created {open_uk_network['OPEN_UK_Network_Name']}.")


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0002_seed_abstraction_levels"),
    ]

    operations = [
        migrations.RunPython(ods_codes_to_abstraction_levels),
    ]
