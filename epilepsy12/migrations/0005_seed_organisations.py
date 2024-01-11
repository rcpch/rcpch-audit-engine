# standard library imports
import logging

# Django imports
from django.contrib.gis.geos import Point
from django.db import migrations
from django.utils import timezone
from django.contrib.gis.db.models import Q

from ..constants import (
    RCPCH_ORGANISATIONS,
    INTEGRATED_CARE_BOARDS_LOCAL_AUTHORITIES,
    OPEN_UK_NETWORKS_TRUSTS,
)

# Logging setup
logger = logging.getLogger(__name__)


def seed_organisations(apps, schema_editor):
    """
    Seed function which populates the Organisation table from JSON.
    This instead uses a list provided by RCPCH E12 team of all organisations in England
    and Wales that care for children with Epilepsy - community paediatrics and hospital paediatrics
    in the same trust are counted as one organisation.
    """

    # Get models
    Organisation = apps.get_model("epilepsy12", "Organisation")
    Trust = apps.get_model("epilepsy12", "Trust")
    LocalHealthBoard = apps.get_model("epilepsy12", "LocalHealthBoard")
    IntegratedCareBoard = apps.get_model("epilepsy12", "IntegratedCareBoard")
    NHSEnglandRegion = apps.get_model("epilepsy12", "NHSEnglandRegion")
    LondonBorough = apps.get_model("epilepsy12", "LondonBorough")
    OPENUKNetwork = apps.get_model("epilepsy12", "OPENUKNetwork")
    Country = apps.get_model("epilepsy12", "Country")
    england = Country.objects.get(boundary_identifier="E92000001")
    wales = Country.objects.get(boundary_identifier="W92000004")

    if Organisation.objects.all().count() >= 330:
        logger.debug(
            "\033[31m 329 RCPCH organisations already seeded. Skipping... \033[31m",
        )
    else:
        logger.debug("\033[31m Adding new RCPCH organisations... \033[31m")

        for added, rcpch_organisation in enumerate(RCPCH_ORGANISATIONS):
            # Apply longitude and latitude data, if exists
            new_point = None
            try:
                latitude = float(rcpch_organisation["Latitude"])
            except:
                latitude = None
            try:
                longitude = float(rcpch_organisation["Longitude"])
            except:
                latitude = None

            if longitude and latitude:
                new_point = Point(x=longitude, y=latitude)

            # Date-stamps the Organisation information (this data was supplied on 19.04.2023)
            # update_date = datetime(year=2023, month=4, day=19)
            # timezone_aware_update_date = timezone.make_aware(update_date, timezone.utc)

            # Create Organisation instances
            try:
                organisation = Organisation.objects.create(
                    ods_code=rcpch_organisation["OrganisationCode"],
                    name=rcpch_organisation["OrganisationName"],
                    website=rcpch_organisation["Website"],
                    address1=rcpch_organisation["Address1"],
                    address2=rcpch_organisation["Address2"],
                    address3=rcpch_organisation["Address3"],
                    city=rcpch_organisation["City"],
                    county=rcpch_organisation["County"],
                    latitude=latitude,
                    longitude=longitude,
                    postcode=rcpch_organisation["Postcode"],
                    geocode_coordinates=new_point,
                    telephone=rcpch_organisation["Phone"],
                )
                # add trust or local health board
                if (
                    LocalHealthBoard.objects.filter(
                        ods_code=rcpch_organisation["ParentODSCode"]
                    ).count()
                    > 0
                ):
                    local_health_board = LocalHealthBoard.objects.get(
                        ods_code=rcpch_organisation["ParentODSCode"]
                    )
                    organisation.local_health_board = local_health_board
                    organisation.country = wales
                elif (
                    Trust.objects.filter(
                        ods_code=rcpch_organisation["ParentODSCode"]
                    ).count()
                    > 0
                ):
                    trust = Trust.objects.get(
                        ods_code=rcpch_organisation["ParentODSCode"]
                    )
                    organisation.trust = trust
                    organisation.country = england

                else:
                    raise Exception(
                        f"No Match! {rcpch_organisation['OrganisationName']} has no parent organisation."
                    )

                # add london boroughs
                if rcpch_organisation["City"] == "LONDON":
                    try:
                        london_borough = LondonBorough.objects.get(
                            gss_code=rcpch_organisation["LocalAuthority"]
                        )
                        organisation.london_borough = london_borough
                    except Exception as e:
                        logger.debug(
                            f"Unable to save London Borough {rcpch_organisation['LocalAuthority']}"
                        )
                        pass

                organisation.save()
                logger.debug(f"{added+1}: {rcpch_organisation['OrganisationName']}")
            except Exception as error:
                logger.debug(
                    f"Unable to save {rcpch_organisation['OrganisationName']}: {error}"
                )

        logger.debug(f"{added+1} organisations added.")

    logger.debug(
        "\033[31m Updating RCPCH organisations with ICB, NHS England relationships... \033[31m",
    )
    # add integrated care boards and NHS regions to organisations
    for added, icb_trust in enumerate(INTEGRATED_CARE_BOARDS_LOCAL_AUTHORITIES):
        try:
            icb = IntegratedCareBoard.objects.get(ods_code=icb_trust["ODS ICB Code"])
        except Exception as error:
            logger.debug(
                f"Could not match ICB ODS Code {icb_trust['ODS ICB Code']} with that in Trust table."
            )

        try:
            trust = Trust.objects.get(ods_code=icb_trust["ODS Trust Code"])
        except Exception as error:
            logger.debug(
                f"Could not match Trust ODS Code {icb_trust['ODS Trust Code']} with that in Trust table."
            )

        try:
            nhs_england_region = NHSEnglandRegion.objects.get(
                region_code=icb_trust["NHS England Region Code"]
            )
        except Exception as error:
            logger.debug(
                f"Could not match NHS Region GSS Code {icb_trust['NHS England Region Code']} with that in the NHS England Region table."
            )

        update_fields = {
            "integrated_care_board": icb,
            "nhs_england_region": nhs_england_region,
        }
        # if icb_trust[]
        # update all organisations associated with this trust with this ICB
        try:
            Organisation.objects.filter(trust=trust).update(**update_fields)
        except Exception as error:
            logger.debug(
                f"Unable to find {icb_trust['ODS Trust Code']} when updating {icb_trust['ODS ICB Code']} ICB and {icb_trust['NHS England Region Code']} NHS England Region!"
            )
    logger.debug(
        f"\033[31m Updated {added+1} RCPCH organisations with ICB, NHS England relationships... \033[31m",
    )

    logger.debug(
        "\033[31m Updating all RCPCH organisations with OPEN UK network relationships... \033[31m",
    )
    # openuk_network
    for added, trust_openuk_network in enumerate(OPEN_UK_NETWORKS_TRUSTS):
        query_term = Q()
        if Trust.objects.filter(
            ods_code=trust_openuk_network["ods trust code"]
        ).exists():
            query_term = Q(
                trust=Trust.objects.get(ods_code=trust_openuk_network["ods trust code"])
            )
        elif LocalHealthBoard.objects.filter(
            ods_code=trust_openuk_network["ods trust code"]
        ).exists():
            query_term = Q(
                local_health_board=LocalHealthBoard.objects.get(
                    ods_code=trust_openuk_network["ods trust code"]
                )
            )
        else:
            raise Exception(f"{trust_openuk_network['ods trust code']} error")

        openuk_network = OPENUKNetwork.objects.get(
            boundary_identifier=trust_openuk_network["OPEN UK Network Code"]
        )
        # upoate the OPENUK netowork for all the Organisations in this trust
        Organisation.objects.filter(query_term).update(openuk_network=openuk_network)
    logger.debug(
        f"\033[31m Updated {added+1} RCPCH organisations with OPENUK relationships... \033[31m",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0004_seed_trusts"),
    ]

    operations = [migrations.RunPython(seed_organisations)]
