# python imports
from typing import Literal

# django imports
from django.contrib.gis.db.models import Q
from django.apps import apps

from epilepsy12.general_functions.audit_period_hierarchy import (
    resolve_period_parent_for_field,
    get_period_organisation_ids,
    expand_organisation_ids_via_identity,
)

# Maps abstraction_level strings used by the view layer to the FK field
# names on Organisation / AuditPeriodOrganisation.
_PARENT_FIELD = {
    "trust": "trust",
    "local_health_board": "local_health_board",
    "icb": "integrated_care_board",
    "nhs_england_region": "nhs_england_region",
    "open_uk": "openuk_network",
    "country": "country",
}


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
    audit_period=None,
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
    audit_period: optional AuditPeriod instance. When provided, the trust/LHB/ICB/region/network/country parent is
    resolved per-cohort from the approved AuditPeriodOrganisation membership (with fallback to the current parent
    when no approved membership exists). The organisation set is also expanded through the OrganisationIdentity chain
    so that cases from inactive predecessor organisations remain visible. When None (the default), the function
    behaves exactly as before — using the live Organisation.trust / .local_health_board / etc.

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
            & Q(registration__audit_period__cohort_number=cohort)
        ).all()
    else:
        all_cases_for_cohort = Case.objects.filter(
            Q(registration__isnull=False) & Q(registration__audit_period__cohort_number=cohort)
        ).all()

    # --- Period-aware organisation-set resolution -------------------------
    #
    # When audit_period is provided, the parent for each abstraction level
    # is resolved per-cohort from the approved AuditPeriodOrganisation
    # membership (with fallback to the current parent when no approved
    # membership exists).  The organisation set is expanded through the
    # OrganisationIdentity chain so that cases from inactive predecessor
    # organisations remain visible.
    #
    # When audit_period is None, the original live-parent behaviour is used
    # — the function behaves exactly as before.

    site_active_q = (
        Q(epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True)
        & Q(epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True)
    )

    if abstraction_level == "organisation":
        if audit_period is not None:
            org_ids = expand_organisation_ids_via_identity(
                {organisation_instance.pk}
            )
            q_filter = Q(epilepsy12_sites__organisation__pk__in=org_ids) & site_active_q
        else:
            q_filter = (
                Q(epilepsy12_sites__organisation__pk=organisation_instance.pk)
                & site_active_q
            )

    elif abstraction_level in _PARENT_FIELD:
        parent_field = _PARENT_FIELD[abstraction_level]
        current_parent = getattr(organisation_instance, parent_field, None)

        if current_parent is None and abstraction_level in ("trust", "local_health_board"):
            return all_cases_for_cohort

        if audit_period is not None:
            period_parent, is_period_correct = resolve_period_parent_for_field(
                organisation_instance, audit_period, parent_field
            )
            if is_period_correct and period_parent is not None:
                org_ids = get_period_organisation_ids(
                    period_parent, audit_period, parent_field
                )
                if org_ids:
                    q_filter = (
                        Q(epilepsy12_sites__organisation__pk__in=org_ids)
                        & site_active_q
                    )
                else:
                    # No approved memberships for this parent/period — fall
                    # back to current parent.
                    q_filter = _current_parent_filter(
                        abstraction_level, organisation_instance, site_active_q
                    )
            else:
                # Fallback: no approved membership — use current parent.
                q_filter = _current_parent_filter(
                    abstraction_level, organisation_instance, site_active_q
                )
        else:
            q_filter = _current_parent_filter(
                abstraction_level, organisation_instance, site_active_q
            )

    elif abstraction_level == "national":
        q_filter = site_active_q

    else:
        raise ValueError(
            f"Incorrect or invalid abstraction error {abstraction_level} supplied."
        )

    return all_cases_for_cohort.filter(q_filter)


def _current_parent_filter(abstraction_level, organisation_instance, site_active_q):
    """Build the Q filter for a given abstraction level using the current
    (live) parent.  This is the pre-foundation behaviour, used both when
    audit_period is None and as the fallback when no approved
    AuditPeriodOrganisation membership exists.
    """
    parent_field = _PARENT_FIELD[abstraction_level]
    current_parent = getattr(organisation_instance, parent_field, None)

    if current_parent is None:
        # No parent for this abstraction level (e.g. Wales has no ICB).
        # Return a Q that matches nothing — the caller already handles
        # the trust/LHB case by returning early; this covers ICB/region/etc.
        return Q(pk__in=[])

    if abstraction_level == "trust":
        return (
            Q(epilepsy12_sites__organisation__trust__ods_code=current_parent.ods_code)
            & site_active_q
        )
    elif abstraction_level == "local_health_board":
        return (
            Q(
                epilepsy12_sites__organisation__local_health_board__ods_code=current_parent.ods_code
            )
            & site_active_q
        )
    elif abstraction_level == "icb":
        return (
            Q(
                epilepsy12_sites__organisation__integrated_care_board__ods_code=current_parent.ods_code
            )
            & site_active_q
        )
    elif abstraction_level == "nhs_england_region":
        return (
            Q(
                epilepsy12_sites__organisation__nhs_england_region__region_code=current_parent.region_code
            )
            & Q(
                epilepsy12_sites__organisation__country__boundary_identifier=organisation_instance.country.boundary_identifier
            )
            & site_active_q
        )
    elif abstraction_level == "open_uk":
        return (
            Q(
                epilepsy12_sites__organisation__openuk_network__boundary_identifier=current_parent.boundary_identifier
            )
            & site_active_q
        )
    elif abstraction_level == "country":
        return (
            Q(
                epilepsy12_sites__organisation__country__boundary_identifier=current_parent.boundary_identifier
            )
            & site_active_q
        )
    else:
        raise ValueError(
            f"Incorrect or invalid abstraction error {abstraction_level} supplied."
        )


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
        get_all_trusts.objects.order_by("name")
        .values_list("ods_code", "name")
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
