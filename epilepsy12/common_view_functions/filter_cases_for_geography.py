from django.apps import apps
from django.db.models import Q
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
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
    filtered_cases = (
        Case.objects.filter(
            ~Q(postcode__in=UNKNOWN_POSTCODES_NO_SPACES),
            registration__isnull=False,
            registration__cohort=cohort,
            site__organisation=organisation,
            site__site_is_actively_involved_in_epilepsy_care=True,
            site__site_is_primary_centre_of_epilepsy_care=True,
        )
        .annotate(
            distance_from_lead_organisation=Distance(
                "location_wgs84",
                Point(
                    organisation.longitude,
                    organisation.latitude,
                    srid=4326,
                ),
            )
        )
        .values(
            "pk",
            "site__organisation__name",
            "first_name",
            "surname",
            "location_bng",
            "location_wgs84",
            "distance_from_lead_organisation",
        )
    )

    return filtered_cases
