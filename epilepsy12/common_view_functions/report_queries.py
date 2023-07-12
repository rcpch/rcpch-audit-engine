# python imports
from typing import Literal

# django imports
from django.contrib.gis.db.models import Q
from django.apps import apps

# E12 imports
# from ..models import (
#     Case,
#     Organisation,
#     NHSRegionEntity,
#     OPENUKNetworkEntity,
#     IntegratedCareBoardEntity,
#     ONSCountryEntity,
# )


def all_registered_cases_for_cohort_and_abstraction_level(
    organisation_instance,
    cohort,
    case_complete=True,
    abstraction_level: Literal[
        "organisation", "trust", "icb", "nhs_region", "open_uk", "country", "national"
    ] = "organisation",
):
    """
    Returns all Cases that have been registered for a given cohort at a given abstration level.
    It can return cases that are only registered in E12 for a given cohort but have not yet completed the return, or
    cases that are both registered and have also completed all required fields in the return.
    Parameters accepted:
    Organisation instance
    Cohort - this is an integer
    case_complete: a boolean flag denoting that the case is registered in Epilepsy12 and a fully completed audit return is available
    abstraction level: string, one of ['organisation', 'trust', 'icb', 'nhs_region', 'open_uk', 'country', 'national']

    Note that all these children will by definition have epilepsy, since a cohort cannot be allocated without the clinician confirming
    1. the child has epilepsy
    2. the first paediatric assessment falls within the the dates for that cohort
    3. a lead E12 site has been allocated
    """
    Case = apps.get_model("epilepsy12", "Case")

    if case_complete:
        all_cases_for_cohort = Case.objects.filter(
            Q(registration__isnull=False)
            & Q(registration__audit_progress__registration_complete=True)
            & Q(registration__audit_progress__first_paediatric_assessment_complete=True)
            & Q(registration__audit_progress__assessment_complete=True)
            & Q(registration__audit_progress__epilepsy_context_complete=True)
            & Q(registration__audit_progress__multiaxial_diagnosis_complete=True)
            & Q(registration__audit_progress__investigations_complete=True)
            & Q(registration__audit_progress__management_complete=True)
            & Q(registration__cohort=cohort)
        ).all()
    else:
        all_cases_for_cohort = Case.objects.filter(
            Q(registration__isnull=False) & Q(registration__cohort=cohort)
        ).all()

    if abstraction_level == "organisation":
        q_filter = (
            Q(site__organisation__pk=organisation_instance.pk)
            & Q(site__site_is_actively_involved_in_epilepsy_care=True)
            & Q(site__site_is_primary_centre_of_epilepsy_care=True)
        )
    elif abstraction_level == "trust":
        q_filter = (
            Q(
                site__organisation__ParentOrganisation_ODSCode=organisation_instance.ParentOrganisation_ODSCode
            )
            & Q(site__site_is_actively_involved_in_epilepsy_care=True)
            & Q(site__site_is_primary_centre_of_epilepsy_care=True)
        )
    elif abstraction_level == "icb":
        if organisation_instance.integrated_care_board is not None:
            """
            Wales has no ICBs
            """
            q_filter = (
                Q(
                    site__organisation__integrated_care_board__ODS_ICB_Code=organisation_instance.integrated_care_board.ODS_ICB_Code
                )
                & Q(site__site_is_actively_involved_in_epilepsy_care=True)
                & Q(site__site_is_primary_centre_of_epilepsy_care=True)
            )
        else:
            return all_cases_for_cohort
    elif abstraction_level == "nhs_region":
        """
        Wales has no NHS regions
        """
        if organisation_instance.nhs_region is not None:
            q_filter = (
                Q(
                    site__organisation__nhs_region__NHS_Region_Code=organisation_instance.nhs_region.NHS_Region_Code
                )
                & Q(
                    site__organisation__ons_region__ons_country__Country_ONS_Name=organisation_instance.ons_region.ons_country.Country_ONS_Name
                )
                & Q(site__site_is_actively_involved_in_epilepsy_care=True)
                & Q(site__site_is_primary_centre_of_epilepsy_care=True)
            )
        else:
            return all_cases_for_cohort
    elif abstraction_level == "open_uk":
        q_filter = (
            Q(
                site__organisation__openuk_network__OPEN_UK_Network_Code=organisation_instance.openuk_network.OPEN_UK_Network_Code
            )
            & Q(site__site_is_actively_involved_in_epilepsy_care=True)
            & Q(site__site_is_primary_centre_of_epilepsy_care=True)
        )
    elif abstraction_level == "country":
        q_filter = (
            Q(
                site__organisation__ons_region__ons_country=organisation_instance.ons_region.ons_country
            )
            & Q(site__site_is_actively_involved_in_epilepsy_care=True)
            & Q(site__site_is_primary_centre_of_epilepsy_care=True)
        )
    elif abstraction_level == "national":
        q_filter = Q(site__site_is_actively_involved_in_epilepsy_care=True) & Q(
            site__site_is_primary_centre_of_epilepsy_care=True
        )
    else:
        raise ValueError(
            f"Incorrect or invalid abstraction error f{abstraction_level} supplied."
        )

    return all_cases_for_cohort.filter(q_filter)


def get_all_countries():
    """
    Returns a list of all Countries

    """
    ONSCountryEntity = apps.get_model("epilepsy12", "ONSCountryEntity")
    return ONSCountryEntity.objects.order_by("Country_ONS_Name")


def get_all_nhs_regions():
    """
    Returns a list of all NHS Regions
    [('Y56', 'London'), ('Y58', 'South West'), ('Y59', 'South East'), ('Y60', 'Midlands (Y60)'), ('Y61', 'East of England'), ('Y62', 'North West'), ('Y63', 'North East and Yorkshire'), (None, None)]
    """
    NHSRegionEntity = apps.get_model("epilepsy12", "NHSRegionEntity")
    return NHSRegionEntity.objects.filter(year=2019).order_by(
        "NHS_Region", "NHS_Region_Code"
    )


def get_all_open_uk_regions():
    """
    Returns a list of all OPEN UK Networks
    [('BRPNF', 'Birmingham Regional Paediatric Neurology Forum'), ('CEWT', "Children's Epilepsy Workstream in Trent"), ('EPEN', 'Eastern Paediatric Epilepsy Network'), ('EPIC', "Mersey and North Wales network 'Epilepsy In Childhood' interest group"), ('NTPEN', 'North Thames Paediatric Epilepsy Network'), ('NWEIG', "North West Children and Young People's Epilepsy Interest Group"), ('ORENG', 'Oxford region epilepsy interest group'), ('PENNEC', 'Paediatric Epilepsy Network for the North East and Cumbria'), ('SETPEG', 'South East Thames Paediatric Epilepsy Group'), ('SETPEG', 'SSouth East Thames Paediatric Epilepsy Group'), ('SWEP', 'South Wales Epilepsy Forum'), ('SWIPE', 'South West Interest Group Paediatric Epilepsy'), ('SWTPEG', 'South West Thames Paediatric Epilepsy Group'), ('TEN', 'Trent Epilepsy Network'), ('WPNN', 'Wessex Paediatric Neurosciences Network'), ('YPEN', 'Yorkshire Paediatric Neurology Network'), (None, None)]
    """
    OPENUKNetworkEntity = apps.get_model("epilepsy12", "OPENUKNetworkEntity")
    return OPENUKNetworkEntity.objects.order_by("OPEN_UK_Network_Name", "country")


def get_all_icbs():
    """
    Returns a list of all Integrated Care Boards
    """
    IntegratedCareBoardEntity = apps.get_model(
        "epilepsy12", "IntegratedCareBoardEntity"
    )
    return IntegratedCareBoardEntity.objects.order_by("ICB_Name")


def get_all_trusts():
    """
    Returns a list of all Trusts
    """
    Organisation = apps.get_model("epilepsy12", "Organisation")
    return (
        Organisation.objects.order_by(
            "ParentOrganisation_OrganisationName", "ParentOrganisation_ODSCode"
        )
        .values_list(
            "ParentOrganisation_ODSCode", "ParentOrganisation_OrganisationName"
        )
        .distinct()
    )


def get_all_organisations():
    """
    Returns a list of all Organisations
    """
    Organisation = apps.get_model("epilepsy12", "Organisation")
    return (
        Organisation.objects.order_by("OrganisationName", "ODSCode")
        .values_list("OrganisationName", "ODSCode")
        .distinct()
    )
