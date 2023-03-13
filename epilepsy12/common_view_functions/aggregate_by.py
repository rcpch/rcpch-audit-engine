# Django imports
from django.db.models import Q, F, Count, Sum, Avg, When, Value, CharField, PositiveSmallIntegerField, Case as DJANGO_CASE

# E12 imports
from epilepsy12.constants import ETHNICITIES, SEX_TYPE
from ..models import Case
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


def aggregate_all_eligible_kpi_fields(filtered_cases, kpi_measure=None):
    """
    Returns a dictionary of all KPI fields with aggregation for each measure ready to pass
    into a related model. If an individual measure is passed in, only that measure will be aggregated.
    It can only be used by a model which has a relationship with registration (but not registration itself)
    Returned fields include sum of all eligible KPI measures (identified as having an individual score of 1 or 0)
    for that registration as well as average score of the same and total number KPIs.
    A KPI score of 2 is excluded as not eligible for that measure.
    """

    all_kpi_measures = [
        'paediatrician_with_expertise_in_epilepsies',
        'epilepsy_specialist_nurse',
        'tertiary_input',
        'epilepsy_surgery_referral',
        'ecg',
        'mri',
        'assessment_of_mental_health_issues',
        'mental_health_support',
        'sodium_valproate',
        'comprehensive_care_planning_agreement',
        'patient_held_individualised_epilepsy_document',
        'patient_carer_parent_agreement_to_the_care_planning',
        'care_planning_has_been_updated_when_necessary',
        'comprehensive_care_planning_content',
        'parental_prolonged_seizures_care_plan',
        'water_safety',
        'first_aid',
        'general_participation_and_risk',
        'service_contact_details',
        'sudep',
        'school_individual_healthcare_plan'
    ]

    aggregation_fields = {}

    if kpi_measure:
        # a single measure selected for aggregation

        q_objects = Q(**{f'registration__kpi__{kpi_measure}__lt': 2}
                      ) & Q(**{f'registration__kpi__{kpi_measure}__isnull': False})
        f_objects = F(f'registration__kpi__{kpi_measure}')

        # sum this measure
        aggregation_fields[f'{kpi_measure}'] = Sum(
            DJANGO_CASE(When(q_objects,
                        then=f_objects), default=None)
        )
        # average of the sum of this measure
        aggregation_fields[f'{kpi_measure}_average'] = Avg(
            DJANGO_CASE(When(q_objects,
                        then=f_objects), default=None))
        # total cases scored for this measure
        aggregation_fields['total_number_of_cases'] = Count(
            DJANGO_CASE(When(q_objects,
                        then=f_objects), default=None))
    else:
        # aggregate all measures

        for measure in all_kpi_measures:
            # filter cases for all kpi with a score < 2
            q_objects = Q(**{f'registration__kpi__{measure}__lt': 2}
                          ) & Q(**{f'registration__kpi__{measure}__isnull': False})
            f_objects = F(f'registration__kpi__{measure}')

            # sum this measure
            aggregation_fields[f'{measure}'] = Sum(
                DJANGO_CASE(When(q_objects,
                                 then=f_objects), default=0))
            # average of the sum of this measure
            aggregation_fields[f'{measure}_average'] = Avg(
                DJANGO_CASE(When(q_objects,
                                 then=f_objects), default=0))
            # total cases scored for this measure
            aggregation_fields[f'{measure}_total'] = Count(
                DJANGO_CASE(When(q_objects,
                                 then=f_objects), default=0))
        # total_cases scored for all measures
        aggregation_fields['total_number_of_cases'] = Count(
            DJANGO_CASE(When(q_objects,
                        then=f_objects), default=0))

    return filtered_cases.aggregate(**aggregation_fields)
