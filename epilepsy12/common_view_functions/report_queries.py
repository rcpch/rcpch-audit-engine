# python imports
from typing import Literal

# django imports
from django.contrib.gis.db.models import Q
from django.apps import apps


def all_registered_cases_for_cohort_and_abstraction_level(
    organisation_instance,
    cohort,
    case_complete=True,
    abstraction_level: Literal[
        "organisation",
        "trust",
        "local_health_board",
        "icb",
        "nhs_england_region",
        "open_uk",
        "country",
        "national",
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
        if organisation_instance.trust is not None:
            q_filter = (
                Q(
                    site__organisation__trust__ods_code=organisation_instance.trust.ods_code
                )
                & Q(site__site_is_actively_involved_in_epilepsy_care=True)
                & Q(site__site_is_primary_centre_of_epilepsy_care=True)
            )
        else:
            return all_cases_for_cohort
    elif abstraction_level == "local_health_board":
        if organisation_instance.local_health_board is not None:
            q_filter = (
                Q(
                    site__organisation__local_health_board__ods_code=organisation_instance.local_health_board.ods_code
                )
                & Q(site__site_is_actively_involved_in_epilepsy_care=True)
                & Q(site__site_is_primary_centre_of_epilepsy_care=True)
            )
        else:
            return all_cases_for_cohort
    elif abstraction_level == "icb":
        if organisation_instance.integrated_care_board is not None:
            """
            Wales has no ICBs
            """
            q_filter = (
                Q(
                    site__organisation__integrated_care_board__ods_code=organisation_instance.integrated_care_board.ods_code
                )
                & Q(site__site_is_actively_involved_in_epilepsy_care=True)
                & Q(site__site_is_primary_centre_of_epilepsy_care=True)
            )
        else:
            return all_cases_for_cohort
    elif abstraction_level == "nhs_england_region":
        """
        Wales has no NHS regions
        """
        if organisation_instance.nhs_england_region is not None:
            q_filter = (
                Q(
                    site__organisation__nhs_england_region__region_code=organisation_instance.nhs_england_region.region_code
                )
                & Q(
                    site__organisation__country__boundary_identifier=organisation_instance.country.boundary_identifier
                )
                & Q(site__site_is_actively_involved_in_epilepsy_care=True)
                & Q(site__site_is_primary_centre_of_epilepsy_care=True)
            )
        else:
            return all_cases_for_cohort
    elif abstraction_level == "open_uk":
        q_filter = (
            Q(
                site__organisation__openuk_network__boundary_identifier=organisation_instance.openuk_network.boundary_identifier
            )
            & Q(site__site_is_actively_involved_in_epilepsy_care=True)
            & Q(site__site_is_primary_centre_of_epilepsy_care=True)
        )
    elif abstraction_level == "country":
        q_filter = (
            Q(
                site__organisation__country__boundary_identifier=organisation_instance.country.boundary_identifier
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
    Country = apps.get_model("epilepsy12", "Country")
    return Country.objects.order_by("name")


def get_all_nhs_regions():
    """
    Returns a list of all NHS Regions.

    <QuerySet [<NHSEnglandRegion: Aneurin Bevan University Health Board>, <NHSEnglandRegion: Betsi Cadwaladr University Health Board>, <NHSEnglandRegion: Cardiff and Vale University Health Board>, <NHSEnglandRegion: Cwm Taf Morgannwg University Health Board>, <NHSEnglandRegion: East of England>, <NHSEnglandRegion: Hywel Dda University Health Board>, <NHSEnglandRegion: London>, <NHSEnglandRegion: Midlands (Y60)>, <NHSEnglandRegion: North East and Yorkshire>, <NHSEnglandRegion: North West>, <NHSEnglandRegion: Powys Teaching Health Board>, <NHSEnglandRegion: South East>, <NHSEnglandRegion: South West>, <NHSEnglandRegion: Swansea Bay University Health Board>]>
    """
    NHSEnglandRegion = apps.get_model("epilepsy12", "NHSEnglandRegion")

    return NHSEnglandRegion.objects.order_by("name")


def get_all_open_uk_regions():
    """
    Returns a list of all OPEN UK Networks
    [('BRPNF', 'Birmingham Regional Paediatric Neurology Forum'), ('CEWT', "Children's Epilepsy Workstream in Trent"), ('EPEN', 'Eastern Paediatric Epilepsy Network'), ('EPIC', "Mersey and North Wales network 'Epilepsy In Childhood' interest group"), ('NTPEN', 'North Thames Paediatric Epilepsy Network'), ('NWEIG', "North West Children and Young People's Epilepsy Interest Group"), ('ORENG', 'Oxford region epilepsy interest group'), ('PENNEC', 'Paediatric Epilepsy Network for the North East and Cumbria'), ('SETPEG', 'South East Thames Paediatric Epilepsy Group'), ('SETPEG', 'SSouth East Thames Paediatric Epilepsy Group'), ('SWEP', 'South Wales Epilepsy Forum'), ('SWIPE', 'South West Interest Group Paediatric Epilepsy'), ('SWTPEG', 'South West Thames Paediatric Epilepsy Group'), ('TEN', 'Trent Epilepsy Network'), ('WPNN', 'Wessex Paediatric Neurosciences Network'), ('YPEN', 'Yorkshire Paediatric Neurology Network'), (None, None)]
    """
    OPENUKNetwork = apps.get_model("epilepsy12", "OPENUKNetwork")
    return OPENUKNetwork.objects.order_by("name", "country")


def get_all_icbs():
    """
    Returns a list of all Integrated Care Boards
    """
    IntegratedCareBoard = apps.get_model("epilepsy12", "IntegratedCareBoard")
    return IntegratedCareBoard.objects.order_by("name")


def get_all_trusts():
    """
    Returns a list of all Trusts
    """
    Trust = apps.get_model("epilepsy12", "Trust")
    return (
        get_all_trusts.objects.order_by("trust_name")
        .values_list("ods_code", "trust_name")
        .distinct()
    )


def get_all_organisations():
    """
    Returns a list of all Organisations
    """
    Organisation = apps.get_model("epilepsy12", "Organisation")
    return (
        Organisation.objects.order_by("name", "ods_code")
        .values("name", "ods_code")
        .distinct()
    )
