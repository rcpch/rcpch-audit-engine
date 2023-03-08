# python imports

# django imports
from django.db.models import Q

# E12 imports
from ..models import Case
from ..general_functions import get_current_cohort_data


def all_registered_and_complete_cases_for_hospital(hospital_instance):
    """
    Returns all Cases that have been registered and completed audit returns for the current cohort at a given hospital
    """
    return Case.objects.filter(
        Q(hospital_trusts__OrganisationName__contains=hospital_instance.OrganisationName) &
        Q(registration__isnull=False) &
        Q(registration__audit_progress__registration_complete=True) &
        Q(registration__audit_progress__first_paediatric_assessment_complete=True) &
        Q(registration__audit_progress__assessment_complete=True) &
        Q(registration__audit_progress__epilepsy_context_complete=True) &
        Q(registration__audit_progress__multiaxial_diagnosis_complete=True) &
        Q(registration__audit_progress__investigations_complete=True) &
        Q(registration__audit_progress__management_complete=True)
    ).all()


def all_registered_and_complete_cases_for_hospital_trust(hospital_instance):
    """
    Returns all Cases that have been registered and completed audit returns for the current cohort at a given hospital
    """
    cohort_data = get_current_cohort_data()
    return Case.objects.filter(
        Q(hospital_trusts__OrganisationName__contains=hospital_instance.ParentName) &
        Q(registration__isnull=False) &
        Q(registration__audit_progress__registration_complete=True) &
        Q(registration__audit_progress__first_paediatric_assessment_complete=True) &
        Q(registration__audit_progress__assessment_complete=True) &
        Q(registration__audit_progress__epilepsy_context_complete=True) &
        Q(registration__audit_progress__multiaxial_diagnosis_complete=True) &
        Q(registration__audit_progress__investigations_complete=True) &
        Q(registration__audit_progress__management_complete=True) &
        Q(registration__cohort=cohort_data.get('cohort'))
    ).all()


def all_registered_only_cases_for_hospital(hospital_instance):
    """
    Returns all Cases that have been registered and may or may or may not have been completed for the current cohort at a given hospital
    """
    cohort_data = get_current_cohort_data()
    return Case.objects.filter(
        Q(hospital_trusts__OrganisationName__contains=hospital_instance.OrganisationName) &
        Q(registration__cohort=cohort_data.get('cohort'))
    ).all()


def all_registered_only_cases_for_hospital_trust(hospital_instance):
    """
    Returns all Cases that have been registered and may or may or may not have been completed for the current cohort at a given hospital Trust
    """
    cohort_data = get_current_cohort_data()
    return Case.objects.filter(
        Q(hospital_trusts__ParentName__contains=hospital_instance.ParentName) &
        Q(registration__cohort=cohort_data.get('cohort'))
    ).all()
