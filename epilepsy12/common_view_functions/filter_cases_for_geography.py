from django.apps import apps
from django.db.models import Q
from ..constants import EnumAbstractionLevel, UNKNOWN_POSTCODES_NO_SPACES


def filter_all_registered_cases_by_active_lead_site_and_cohort_and_level_of_abstraction(
    organisation,
    cohort,
    enum_abstraction_level: EnumAbstractionLevel = EnumAbstractionLevel.ORGANISATION,
):
    """
    Returns all cases with longitude and latitude within a given organisation or related level of abstraction if supplied (defaults to organisation) and cohort and optionally whether registered or not
    """

    Case = apps.get_model("epilepsy12", "Case")
    filtered_cases = Case.objects.filter(
        ~Q(postcode__in=UNKNOWN_POSTCODES_NO_SPACES),
        registration__isnull=False,
        registration__cohort=cohort,
        site__organisation=organisation,
        site__site_is_actively_involved_in_epilepsy_care=True,
        site__site_is_primary_centre_of_epilepsy_care=True,
    ).values("pk", "location")

    return filtered_cases
