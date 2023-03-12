# python imports
from typing import Literal
# django imports
from django.db.models import Q

# E12 imports
from ..models import Case


def all_registered_cases_for_cohort_and_abstraction_level(hospital_organisation_instance, cohort, case_complete=True, abstraction_level: Literal['organisation', 'trust', 'icb', 'nhs_region', 'open_uk', 'country', 'national'] = 'organisation'):


def all_registered_cases_for_cohort_and_abstraction_level(hospital_organisation_instance, cohort, case_complete=True, abstraction_level: Literal['organisation', 'trust', 'icb', 'nhs_region', 'open_uk', 'country', 'national'] = 'organisation'):
    """
    Returns all Cases that have been registered for a given cohort at a given abstration level.
    It can return cases that are only registered in E12 for a given cohort but have not yet completed the return, or 
    cases that are both registered and have also completed all required fields in the return.
    Parameters accepted:
    HospitalTrust instance
    Cohort - this is an integer
    case_complete: a boolean flag denoting that the case is registered in Epilepsy12 and a fully completed audit return is available
    abstraction level: string, one of ['organisation', 'trust', 'icb', 'nhs_region', 'open_uk', 'country', 'national']

    Note that all these children will by definition have epilepsy, since a cohort cannot be allocated without the clinician confirming
    1. the child has epilepsy
    2. the first paediatric assessment falls within the the dates for that cohort
    3. a lead E12 site has been allocated
    Returns all Cases that have been registered for a given cohort at a given abstration level.
    It can return cases that are only registered in E12 for a given cohort but have not yet completed the return, or 
    cases that are both registered and have also completed all required fields in the return.
    Parameters accepted:
    HospitalTrust instance
    Cohort - this is an integer
    case_complete: a boolean flag denoting that the case is registered in Epilepsy12 and a fully completed audit return is available
    abstraction level: string, one of ['organisation', 'trust', 'icb', 'nhs_region', 'open_uk', 'country', 'national']

    Note that all these children will by definition have epilepsy, since a cohort cannot be allocated without the clinician confirming
    1. the child has epilepsy
    2. the first paediatric assessment falls within the the dates for that cohort
    3. a lead E12 site has been allocated
    """

    if case_complete:
        all_cases_for_cohort = Case.objects.filter(
            Q(registration__isnull=False) &
            Q(registration__audit_progress__registration_complete=True) &
            Q(registration__audit_progress__first_paediatric_assessment_complete=True) &
            Q(registration__audit_progress__assessment_complete=True) &
            Q(registration__audit_progress__epilepsy_context_complete=True) &
            Q(registration__audit_progress__multiaxial_diagnosis_complete=True) &
            Q(registration__audit_progress__investigations_complete=True) &
            Q(registration__audit_progress__management_complete=True) &
            Q(registration__cohort=cohort)
        ).all()
    else:
        all_cases_for_cohort = Case.objects.filter(
            Q(registration__isnull=False) &
            Q(registration__cohort=cohort)
        ).all()
    if case_complete:
        all_cases_for_cohort = Case.objects.filter(
            Q(registration__isnull=False) &
            Q(registration__audit_progress__registration_complete=True) &
            Q(registration__audit_progress__first_paediatric_assessment_complete=True) &
            Q(registration__audit_progress__assessment_complete=True) &
            Q(registration__audit_progress__epilepsy_context_complete=True) &
            Q(registration__audit_progress__multiaxial_diagnosis_complete=True) &
            Q(registration__audit_progress__investigations_complete=True) &
            Q(registration__audit_progress__management_complete=True) &
            Q(registration__cohort=cohort)
        ).all()
    else:
        all_cases_for_cohort = Case.objects.filter(
            Q(registration__isnull=False) &
            Q(registration__cohort=cohort)
        ).all()

    if abstraction_level == 'organisation':
        q_filter = (
            Q(site__hospital_trust__OrganisationID=hospital_organisation_instance.OrganisationID) &
            Q(site__site_is_actively_involved_in_epilepsy_care=True) &
            Q(site__site_is_primary_centre_of_epilepsy_care=True)
        )
    elif abstraction_level == 'trust':
        q_filter = (
            Q(site__hospital_trust__ParentODSCode=hospital_organisation_instance.ParentODSCode) &
            Q(site__site_is_actively_involved_in_epilepsy_care=True) &
            Q(site__site_is_primary_centre_of_epilepsy_care=True)
        )
    elif abstraction_level == 'icb':
        q_filter = (
            Q(site__hospital_trust__ICBODSCode=hospital_organisation_instance.ICBODSCode) &
            Q(site__site_is_actively_involved_in_epilepsy_care=True) &
            Q(site__site_is_primary_centre_of_epilepsy_care=True)
        )
    elif abstraction_level == 'nhs_region':
        q_filter = (
            Q(site__hospital_trust__NHSEnglandRegionCode=hospital_organisation_instance.NHSEnglandRegionCode) &
            Q(site__site_is_actively_involved_in_epilepsy_care=True) &
            Q(site__site_is_primary_centre_of_epilepsy_care=True)
        )
    elif abstraction_level == 'open_uk':
        q_filter = (
            Q(site__hospital_trust__OPENUKNetworkCode=hospital_organisation_instance.OPENUKNetworkCode) &
            Q(site__site_is_actively_involved_in_epilepsy_care=True) &
            Q(site__site_is_primary_centre_of_epilepsy_care=True)
        )
    elif abstraction_level == 'country':
        q_filter = (
            Q(site__hospital_trust__CountryONSCode=hospital_organisation_instance.CountryONSCode) &
            Q(site__site_is_actively_involved_in_epilepsy_care=True) &
            Q(site__site_is_primary_centre_of_epilepsy_care=True)
        )
    elif abstraction_level == 'national':
        q_filter = (
            Q(site__site_is_actively_involved_in_epilepsy_care=True) &
            Q(site__site_is_primary_centre_of_epilepsy_care=True)
        )
    else:
        raise ValueError(
            f"Incorrect or invalid abstraction error f{abstraction_level} supplied.")

    return all_cases_for_cohort.filter(q_filter)
