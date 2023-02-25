# Django imports
from django.db.models import Count, When, Value, CharField, PositiveSmallIntegerField, Case as DJANGO_CASE

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
