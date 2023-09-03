from django.db import migrations
from ..constants import (
    INTEGRATED_CARE_BOARDS,
    NHS_ENGLAND_REGIONS,
    OPEN_UK_NETWORKS,
    LOCAL_HEALTH_BOARDS,
)


def ods_codes_to_abstraction_levels(apps, schema_editor):
    """
    Updates all the abstraction level models with ODS codes
    """
    IntegratedCareBoard = apps.get_model("epilepsy12", "IntegratedCareBoard")
    NHSEnglandRegion = apps.get_model("epilepsy12", "NHSEnglandRegion")
    OPENUKNetwork = apps.get_model("epilepsy12", "OPENUKNetwork")
    LocalHealthBoard = apps.get_model("epilepsy12", "LocalHealthBoard")

    print(
        "\033[38;2;17;167;142m",
        "Updating Integrated Care Boards",
        "\033[38;2;17;167;142m",
    )

    for item in IntegratedCareBoard.objects.all():
        print(item.icb23nm, item.icb23cd)

    for icb in INTEGRATED_CARE_BOARDS:
        # iterates through all 42 ICBs and updates model with ODS code
        if IntegratedCareBoard.objects.filter(icb23cd=icb["gss_code"]).exists():
            # should already exist in the database
            IntegratedCareBoard.objects.filter(icb23cd=icb["gss_code"]).update(
                ods_code=icb["ods_code"]
            )
            print(f"Updated {icb['name']} to include ODS code")
        else:
            raise Exception(
                f"Seeding error. {icb['gss_code']}/{icb['name']} not found in the database to seed."
            )

    print(
        "\033[38;2;17;167;142m",
        "Updating NHS England Regions",
        "\033[38;2;17;167;142m",
    )

    for nhs_england_region in NHS_ENGLAND_REGIONS:
        # iterates through all 42 ICBs and updates model with ODS code
        if NHSEnglandRegion.objects.filter(
            nhser22cd=nhs_england_region["NHS_ENGLAND_REGION_ONS_CODE"]
        ).exists():
            # should already exist in the database
            nhs_england_region_object = NHSEnglandRegion.objects.filter(
                nhser22cd=nhs_england_region["NHS_ENGLAND_REGION_ONS_CODE"]
            ).get()
            nhs_england_region_object.NHS_Region_Code = nhs_england_region[
                "NHS_ENGLAND_REGION_CODE"
            ]
            nhs_england_region_object.save()
            print(
                f"Updated {nhs_england_region['NHS_ENGLAND_REGION_NAME']} to include ODS code"
            )
        else:
            raise Exception("Seeding error. No NHS England region entity to seed.")

    print(
        "\033[38;2;17;167;142m",
        "Updating Local Health Boards",
        "\033[38;2;17;167;142m",
    )

    for local_health_board in LOCAL_HEALTH_BOARDS:
        # iterates through all 42 ICBs and updates model with ODS code
        if LocalHealthBoard.objects.filter(
            lhb22cd=local_health_board["gss_code"]
        ).exists():
            # should already exist in the database
            LocalHealthBoard.objects.filter(
                lhb22cd=local_health_board["gss_code"]
            ).update(ods_code=local_health_board["ods_code"])
            print(f"Updated {local_health_board['health_board']} to include ODS code")
        else:
            raise Exception("Seeding error. No Local Health Board entity to seed.")

    print(
        "\033[38;2;17;167;142m",
        "Updating OPEN UK Networks",
        "\033[38;2;17;167;142m",
    )

    for open_uk_network in OPEN_UK_NETWORKS:
        # iterates through all 42 ICBs and populates table
        if OPENUKNetwork.objects.all().count() == 30:
            # should NOT already exist in the database
            print(
                f"OPEN UK Networks {open_uk_network['OPEN_UK_Network_Name']} have already been added to the database."
            )
            pass
        else:
            OPENUKNetwork.objects.create(
                OPEN_UK_Network_Name=open_uk_network["OPEN_UK_Network_Name"],
                OPEN_UK_Network_Code=open_uk_network["OPEN_UK_Network_Code"],
                country=open_uk_network["country"],
            ).save()
            print(f"Created {open_uk_network['OPEN_UK_Network_Name']}.")


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0002_seed_abstraction_levels"),
    ]

    operations = [
        migrations.RunPython(ods_codes_to_abstraction_levels),
    ]
