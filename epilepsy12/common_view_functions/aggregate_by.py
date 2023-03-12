# Django imports
from django.db.models import Count, Sum, Avg, When, Value, CharField, PositiveSmallIntegerField, Case as DJANGO_CASE

# E12 imports
from epilepsy12.constants import ETHNICITIES, SEX_TYPE
from epilepsy12.models import Case

"""
Reporting
"""


def cases_aggregated_by_sex(selected_hospital):
    # aggregate queries on trust level cases

    sex_long_list = [When(sex=k, then=Value(v))
                     for k, v in SEX_TYPE]

    cases_aggregated_by_sex = (
        Case.objects.filter(
            hospital_trusts__OrganisationName__contains=selected_hospital)
        .values('sex')
        .annotate(
            sex_display=DJANGO_CASE(
                *sex_long_list, output_field=CharField()
            )
        )
        .values('sex_display')
        .annotate(
            sexes=Count('sex')).order_by('sexes')
    )

    return cases_aggregated_by_sex


def cases_aggregated_by_deprivation_score(selected_hospital):
    # aggregate queries on trust level cases

    deprivation_quintiles = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    )

    imd_long_list = [When(index_of_multiple_deprivation_quintile=k, then=Value(v))
                     for k, v in deprivation_quintiles]

    cases_aggregated_by_deprivation = (
        Case.objects.filter(
            hospital_trusts__OrganisationName__contains=selected_hospital)
        .values('index_of_multiple_deprivation_quintile')
        .annotate(
            index_of_multiple_deprivation_quintile_display=DJANGO_CASE(
                *imd_long_list, output_field=PositiveSmallIntegerField()
            )
        )
        .values('index_of_multiple_deprivation_quintile_display')
        .annotate(
            cases_aggregated_by_deprivation=Count('index_of_multiple_deprivation_quintile'))
        .order_by('cases_aggregated_by_deprivation')
    )

    return cases_aggregated_by_deprivation


def cases_aggregated_by_ethnicity(selected_hospital):

    # aggregate queries on trust level cases

    ethnicity_long_list = [When(ethnicity=k, then=Value(v))
                           for k, v in ETHNICITIES]

    cases_aggregated_by_ethnicity = (
        Case.objects.filter(
            hospital_trusts__OrganisationName__contains=selected_hospital)
        .values('ethnicity')
        .annotate(
            ethnicity_display=DJANGO_CASE(
                *ethnicity_long_list, output_field=CharField()
            )
        )
        .values('ethnicity_display')
        .annotate(
            ethnicities=Count('ethnicity')).order_by('ethnicities')
    )

    return cases_aggregated_by_ethnicity


def aggregate_all_kpi_fields_against_registration(kpi_measure=None):
    """
    Returns a dictionary of all KPI fields with aggregation for each measure ready to pass
    into a related model. If an individual measure is passed in, only that measure will be aggregated.
    It can only be used by a model which has a relationship with registration
    Returned fields include sum of totals of all KPI measures for that registration as well as average score
    and total KPIs
    """

    all_kpi_measures = ['paediatrician_with_expertise_in_epilepsies', 'epilepsy_specialist_nurse', 'tertiary_input', 'epilepsy_surgery_referral', 'ecg', 'mri', 'assessment_of_mental_health_issues', 'mental_health_support', 'comprehensive_care_planning_agreement', 'patient_held_individualised_epilepsy_document',
                        'care_planning_has_been_updated_when_necessary', 'comprehensive_care_planning_content', 'parental_prolonged_seizures_care_plan', 'water_safety', 'first_aid', 'general_participation_and_risk', 'service_contact_details', 'sudep', 'school_individual_healthcare_plan']
    aggregation_fields = {}

    if kpi_measure:
        aggregation_fields[f'{kpi_measure}'] = Sum(
            f'registration__kpi__{kpi_measure}')
        aggregation_fields[f'{kpi_measure}_average'] = Avg(
            f'registration__kpi__{kpi_measure}')
        aggregation_fields['total_number_of_cases'] = Count(
            f'registration__kpi__pk')
    else:
        for measure in all_kpi_measures:
            aggregation_fields[f'{measure}'] = Sum(
                f'registration__kpi__{measure}')
            aggregation_fields[f'{measure}_average'] = Avg(
                f'registration__kpi__{measure}')
        aggregation_fields['total_number_of_cases'] = Count(
            f'registration__kpi__pk')

    return aggregation_fields
