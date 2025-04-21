from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db.models import Q

# Third-party imports
import django_filters

from ..constants import KPI_MAP
from epilepsy12.models import Organisation, Case, Site


class CaseFilter(django_filters.FilterSet):
    """
    This is a FilterSet for filtering cases based on various criteria.
    Note that this is used in views that require filtering of cases, not the admin.
    It leverages the CaseFilterMethods utility class for consistent filtering logic.
    """

    AGE_CHOICES = (
        ("under_12", "Under 12 years"),
        ("12_and_over", "12 years and over"),
    )

    age_range = django_filters.ChoiceFilter(
        choices=AGE_CHOICES, method="filter_by_age_range", label="Age Range"
    )

    organisation = django_filters.ModelChoiceFilter(
        queryset=Organisation.objects.filter(
            site__site_is_actively_involved_in_epilepsy_care=True,
            site__site_is_primary_centre_of_epilepsy_care=True,
        ).distinct(),
        method="filter_by_organisation",
    )

    trust_or_health_board = django_filters.CharFilter(
        method="filter_by_trust_or_health_board", label="Trust or Health Board"
    )

    integrated_care_board = django_filters.CharFilter(
        method="filter_by_integrated_care_board", label="Integrated Care Board"
    )

    nhs_england_region = django_filters.CharFilter(
        method="filter_by_nhs_england_region", label="NHS England Region"
    )

    country = django_filters.CharFilter(method="filter_country", label="Country")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add counts to the age range filter choices if we have a queryset
        if hasattr(self, "queryset") and self.queryset is not None:
            counts = CaseFilterMethods.get_age_counts(self.queryset)

            # Update age_range choices with counts
            self.form.fields["age_range"].choices = [
                ("", "---------"),  # Keep the empty choice
                ("under_12", f"Under 12 years ({counts['under_12']})"),
                ("12_and_over", f"12 years and over ({counts['12_and_over']})"),
            ]

    def filter_age_range(self, queryset, name, value):
        """Delegate to CaseFilterMethods for age range filtering"""
        return CaseFilterMethods.filter_by_age_range(queryset, value)

    def filter_organisation(self, queryset, name, value):
        """Delegate to CaseFilterMethods for organisation filtering"""
        return CaseFilterMethods.filter_by_organisation(queryset, value.id)

    def filter_trust_or_health_board(self, queryset, name, value):
        """Delegate to CaseFilterMethods for trust/health board filtering"""
        return CaseFilterMethods.filter_by_trust_or_health_board(queryset, value)

    def filter_integrated_care_board(self, queryset, name, value):
        """Delegate to CaseFilterMethods for ICB filtering"""
        return CaseFilterMethods.filter_by_integrated_care_board(queryset, value)

    def filter_nhs_england_region(self, queryset, name, value):
        """Delegate to CaseFilterMethods for NHS England region filtering"""
        return CaseFilterMethods.filter_by_nhs_england_region(queryset, value)

    def filter_country(self, queryset, name, value):
        """Delegate to CaseFilterMethods for country filtering"""
        return CaseFilterMethods.filter_by_country(queryset, value)

    class Meta:
        model = Case
        fields = [
            "age_range",
            "organisation",
            "trust_or_health_board",
            "integrated_care_board",
            "nhs_england_region",
            "country",
        ]


class CaseFilterMethods:
    """
    This class contains custom methods for filtering cases based on various criteria.
    It is not a FilterSet itself, but rather a utility class that provides static methods
    to be used in the CaseFilter class and in the admin.
    """

    @staticmethod
    def filter_by_age_range(queryset, age_range):
        twelve_years_ago = timezone.now().date() - relativedelta(years=12)

        if age_range == "under_12":
            return queryset.filter(date_of_birth__gt=twelve_years_ago)
        elif age_range == "12_and_over":
            return queryset.filter(date_of_birth__lte=twelve_years_ago)
        return queryset

    @staticmethod
    def get_age_counts(queryset):
        """
        Returns counts of cases under/over 12 years old
        """
        twelve_years_ago = timezone.now().date() - relativedelta(years=12)

        under_12_count = queryset.filter(date_of_birth__gt=twelve_years_ago).count()
        over_12_count = queryset.filter(date_of_birth__lte=twelve_years_ago).count()

        return {"under_12": under_12_count, "12_and_over": over_12_count}

    @staticmethod
    def filter_by_organisation(queryset, organisation_id):
        if not organisation_id:
            return queryset
        return queryset.filter(
            site__organisation_id=organisation_id,
            site__site_is_primary_centre_of_epilepsy_care=True,
            site__site_is_actively_involved_in_epilepsy_care=True,
        )

    @staticmethod
    def get_organisation_counts(queryset, organisation_id):
        """
        Returns counts of cases by organisation (registered and unregistered)
        """
        if not organisation_id:
            return queryset.count()
        return queryset.filter(
            site__organisation_id=organisation_id,
            site__site_is_primary_centre_of_epilepsy_care=True,
            site__site_is_actively_involved_in_epilepsy_care=True,
        ).count()

    @staticmethod
    def filter_by_trust_or_health_board(queryset, value):
        """
        Filter cases by the trust or health board their site is part of.
        Acceptable values are:
        - t_<trust_id> for Trust
        - h_<health_board_id> for Health Board
        This method assumes that the value is a string formatted as "type_id",
        where type can be "t" for Trust or "h" for Health Board.
        The id is the ID of the trust or health board.
        The queryset is filtered to include only cases that are associated with
        the specified trust or health board, and that are part of a site
        that is a primary centre of epilepsy care and is actively involved in
        epilepsy care.
        The queryset is also filtered to include only cases that have a registration.
        """

        value_type, value_id = value.split("_", 1)

        if value_type == "t":
            # Filter by Trust
            return queryset.filter(
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
                site__case__isnull=False,
                site__case__registration__isnull=False,
                site__organisation__trust__id=value_id,
            )
        elif value_type == "h":
            # Filter by Local Health Board
            return queryset.filter(
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
                site__case__isnull=False,
                site__case__registration__isnull=False,
                site__organisation__local_health_board__id=value_id,
            )
        return queryset

    @staticmethod
    def get_trust_or_local_health_board_counts(queryset, value):
        """
        Returns counts of case by trust of local health board - includes cases with no registration
        Accepts a value in the format of "type_id" where type can be "t" for Trust or "h" for Health Board.
        The id is the ID of the trust or health board.
        There queryset is all cases to be filtered to include only cases that are associated with
        the specified trust or health board, and that are part of a site that is a primary centre of
        epilepsy care and is actively involved in epilepsy care.1
        The queryset includes cases that have no registration.
        Acceptable values are:
        - t_<trust_id> for Trust
        - h_<health_board_id> for Health Board
        """
        if not value:
            return 0
        try:
            value_type, value_id = value.split("_", 1)
        except ValueError:
            # Handle the case where value is not in the expected format
            return 0

        if value_type == "t":
            # Filter by Trust
            return (
                queryset.filter(
                    site__site_is_primary_centre_of_epilepsy_care=True,
                    site__site_is_actively_involved_in_epilepsy_care=True,
                    site__organisation__trust__id=value_id,
                )
                .distinct()
                .count()
            )
        elif value_type == "h":
            # Filter by Local Health Board
            return (
                queryset.filter(
                    site__site_is_primary_centre_of_epilepsy_care=True,
                    site__site_is_actively_involved_in_epilepsy_care=True,
                    site__organisation__local_health_board__id=value_id,
                )
                .distinct()
                .count()
            )
        return 0

    @staticmethod
    def filter_by_integrated_care_board(queryset, value):
        """
        Filter cases by the integrated care board their site is part of.
        """
        # value_type and value_id would come from parsing the value parameter
        value_type, value_id = value.split("_", 1)

        if value_type == "i":
            # Filter by Integrate Care Board
            return queryset.filter(
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
                site__case__isnull=False,
                site__case__registration__isnull=False,
                site__organisation__integrated_care_board__id=value_id,
            )
        return queryset

    @staticmethod
    def get_integrated_care_board_counts(queryset, value):
        """
        Returns counts of case by integrated care board - includes cases with no registration
        Accepts a value in the format of "i_<integrated_care_board_id>"
        """
        if not value:
            return 0
        try:
            value_type, value_id = value.split("_", 1)
        except ValueError:
            # Handle the case where value is not in the expected format
            return 0

        if value_type == "i":
            # Filter by Integrated Care Board
            return (
                queryset.filter(
                    site__site_is_primary_centre_of_epilepsy_care=True,
                    site__site_is_actively_involved_in_epilepsy_care=True,
                    site__organisation__integrated_care_board__id=value_id,
                )
                .distinct()
                .count()
            )
        return 0

    @staticmethod
    def filter_by_nhs_england_region(queryset, value):
        """
        Filter cases by the NHS England region their site is part of.
        """
        # value_type and value_id would come from parsing the value parameter
        value_type, value_id = value.split("_", 1)

        if value_type == "n":
            # Filter by NHS England Region
            return queryset.filter(
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
                site__case__isnull=False,
                site__case__registration__isnull=False,
                site__organisation__nhs_england_region__id=value_id,
            )
        return queryset

    def get_nhs_england_region_counts(queryset, value):
        """
        Returns counts of case by NHS England region - includes cases with no registration
        Accepts a value in the format of "nhs_<nhs_england_region_id>"
        """
        if not value:
            return 0
        try:
            value_type, value_id = value.split("_", 1)
        except ValueError:
            # Handle the case where value is not in the expected format
            return 0

        if value_type == "nhs":
            # Filter by NHS England Region
            return (
                queryset.filter(
                    site__site_is_primary_centre_of_epilepsy_care=True,
                    site__site_is_actively_involved_in_epilepsy_care=True,
                    site__organisation__nhs_england_region__id=value_id,
                )
                .distinct()
                .count()
            )
        return 0

    @staticmethod
    def filter_by_country(queryset, value):
        """
        Filter cases by the country their site is part of.
        """
        # value_type and value_id would come from parsing the value parameter
        value_type, value_id = value.split("_", 1)

        if value_type == "c":
            # Filter by Country
            return queryset.filter(
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
                site__case__isnull=False,
                site__case__registration__isnull=False,
                site__organisation__country__id=value_id,
            )
        return queryset

    @staticmethod
    def get_country_counts(queryset, value):
        """
        Returns counts of case by country - includes cases with no registration
        Accepts a value in the format of "c_<country_id>"
        """
        if not value:
            return 0
        try:
            value_type, value_id = value.split("_", 1)
        except ValueError:
            # Handle the case where value is not in the expected format
            return 0

        if value_type == "c":
            # Filter by Country
            return (
                queryset.filter(
                    site__site_is_primary_centre_of_epilepsy_care=True,
                    site__site_is_actively_involved_in_epilepsy_care=True,
                    site__organisation__country__id=value_id,
                )
                .distinct()
                .count()
            )
        return 0

    @staticmethod
    def filter_by_kpi_failed(queryset, kpi_number, cohort, value):
        """
        Filter cases by the KPI failed status.
        """
        # value_type and value_id would come from parsing the value parameter
        value_type, value_id = value.split("_", 1)

        kpi_field = KPI_MAP.get(kpi_number)

        if value_type == "kpi":
            # Filter by KPI failed status

            return queryset.filter(
                Q(f"site__organisation__kpi__{kpi_field}" == 2),
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
                site__case__isnull=False,
                site__case__registration__isnull=False,
                site__organisation__kpi__cohort=cohort,
            )
        return queryset

    def get_kpi_failed_count(queryset, kpi_number, cohort, value):
        """
        Returns counts of case by KPI failed status - includes cases with no registration
        Accepts a value in the format of "kpi_<kpi_number>"
        """
        if not value:
            return 0
        try:
            value_type, value_id = value.split("_", 1)
        except ValueError:
            # Handle the case where value is not in the expected format
            return 0

        kpi_field = KPI_MAP.get(kpi_number)

        if value_type == "kpi":
            # Filter by KPI failed status
            return (
                queryset.filter(
                    Q(f"site__organisation__kpi__{kpi_field}" == 2),
                    site__site_is_primary_centre_of_epilepsy_care=True,
                    site__site_is_actively_involved_in_epilepsy_care=True,
                    site__case__isnull=False,
                    site__case__registration__isnull=False,
                    site__organisation__kpi__cohort=cohort,
                )
                .distinct()
                .count()
            )
        return 0

    @staticmethod
    def apply_all_active_filters(queryset, request, exclude_params=None):
        """
        Apply all the active filters in the request.GET to the queryset.
        Any paraments in the exclude_params list will be ignored.
        This means that the counts for all queries will be applied
        """
        if exclude_params is None:
            exclude_params = []

        # Get all active filters from the request
        for key, value in request.GET.items():
            """
            Check if the key is not in the exclude_params list and if the value is not empty.
            If the key is "p", we skip it as it is used for pagination.
            The keys "organisation", "age_range", "organisation", and "trust_or_local_health_board", "registration__cohort" are handled
            """
            if key not in ["p", exclude_params] and value:
                if key == "organisation":
                    queryset = CaseFilterMethods.filter_by_organisation(
                        queryset=queryset, organisation_id=value
                    )
                elif key == "age_range":
                    queryset = CaseFilterMethods.filter_by_age_range(
                        queryset=queryset, age_range=value
                    )
                elif key == "trust_or_local_health_board":
                    queryset = CaseFilterMethods.filter_by_trust_or_health_board(
                        queryset=queryset, value=value
                    )
                elif key == "integrated_care_board":
                    queryset = CaseFilterMethods.filter_by_integrated_care_board(
                        queryset=queryset, value=value
                    )
                elif key == "nhs_england_region":
                    queryset = CaseFilterMethods.filter_by_nhs_england_region(
                        queryset=queryset, value=value
                    )
                elif key == "country":
                    queryset = CaseFilterMethods.filter_by_country(
                        queryset=queryset, value=value
                    )
                elif key == "registration__cohort":
                    # Filter by registration cohort - includes cases with no registration
                    queryset = queryset.filter(
                        Q(registration__cohort=value)
                        | Q(registration__cohort__isnull=True)
                    )

        return queryset
