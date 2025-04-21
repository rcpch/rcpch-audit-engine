from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db.models import Q
from epilepsy12.models import Organisation, Case, Site

# Third-party imports
import django_filters


class CaseFilter(django_filters.FilterSet):
    """
    This is a FilterSet for filtering cases based on various criteria.
    Note that this is used in views that require filtering of cases, not the admin.
    It draws on the CaseFIlterMethods class for the filter methods.
    """

    AGE_CHOICES = (
        ("under_12", "Under 12 years"),
        ("12_and_over", "12 years and over"),
    )

    age_range = django_filters.ChoiceFilter(
        choices=AGE_CHOICES, method="filter_age_range", label="Age Range"
    )

    organisation = django_filters.ModelChoiceFilter(
        queryset=Organisation.objects.filter(
            site__site_is_actively_involved_in_epilepsy_care=True,
            site__site_is_primary_centre_of_epilepsy_care=True,
        ).distinct(),
        method="filter_organisation",
    )

    def filter_age_range(self, queryset, name, value):
        twelve_years_ago = timezone.now().date() - relativedelta(years=12)

        if value == "under_12":
            return queryset.filter(date_of_birth__gt=twelve_years_ago)
        elif value == "12_and_over":
            return queryset.filter(date_of_birth__lte=twelve_years_ago)
        return queryset

    def filter_organisation(self, queryset, name, value):
        return queryset.filter(
            site__organisation_id=value.id,
            site__site_is_primary_centre_of_epilepsy_care=True,
            site__site_is_actively_involved_in_epilepsy_care=True,
        )

    def filter_trust_or_health_board(self, queryset, name, value):
        # value_type and value_id would come from parsing the value parameter
        value_type, value_id = value.split("_", 1)

        if value_type == "t":
            # Filter by Trust
            return queryset.filter(
                site__organisation__trust_id=value_id,
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
            )
        elif value_type == "h":
            # Filter by Health Board
            return queryset.filter(
                site__organisation__local_health_board_id=value_id,
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
            )
        return queryset

    class Meta:
        model = Case
        fields = ["age_range", "organisation"]


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
    def filter_by_organisation(queryset, organisation_id):
        if not organisation_id:
            return queryset
        return queryset.filter(
            site__organisation_id=organisation_id,
            site__site_is_primary_centre_of_epilepsy_care=True,
            site__site_is_actively_involved_in_epilepsy_care=True,
        )

    @staticmethod
    def filter_by_trust_or_health_board(queryset, value):
        # value_type and value_id would come from parsing the value parameter
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
