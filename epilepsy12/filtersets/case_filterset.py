from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db.models import Q, Count, Sum

# Third-party imports
import django_filters

from ..constants import KPI_MAP, ETHNICITIES, SEX_TYPE
from epilepsy12.models import Organisation, Case


class CaseFilter(django_filters.FilterSet):
    """
    This is a FilterSet for filtering cases based on various criteria.
    Note that this is used in views that require filtering of cases, not the admin.
    It leverages the CaseFilterMethods utility class for consistent filtering logic.
    """

    # simple filters for fields on the Case model
    # Simple field filters
    first_name = django_filters.CharFilter(lookup_expr="icontains")
    surname = django_filters.CharFilter(lookup_expr="icontains")
    nhs_number = django_filters.CharFilter(lookup_expr="icontains")
    unique_reference_number = django_filters.CharFilter(
        field_name="registration__unique_reference_number", lookup_expr="icontains"
    )
    ethnicity = django_filters.ChoiceFilter(choices=ETHNICITIES)
    sex = django_filters.ChoiceFilter(choices=SEX_TYPE)
    date_of_birth = django_filters.DateFilter()
    date_of_birth_range = django_filters.DateFromToRangeFilter(
        field_name="date_of_birth"
    )
    index_of_multiple_deprivation_quintile = django_filters.ChoiceFilter(
        field_name="index_of_multiple_deprivation_quintile"
    )

    # For related fields
    first_paediatric_assessment_date = django_filters.DateFilter(
        field_name="registration__first_paediatric_assessment_date"
    )

    AGE_CHOICES = (
        ("under_12", "Under 12 years"),
        ("12_and_over", "12 years and over"),
    )

    age_range = django_filters.ChoiceFilter(
        choices=AGE_CHOICES, method="filter_by_age_range", label="Age Range"
    )

    """
    Abstraction levels - only visible to the audit team
    """
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

    """
    Progress and Audit level filters
    """
    complete_audit_progress = django_filters.CharFilter(
        method="filter_by_complete_audit_progress", label="Complete Audit Progress"
    )

    incomplete_audit_progress = django_filters.CharFilter(
        method="filter_by_audit_progress_incomplete", label="Incomplete Audit Progress"
    )
    registration_cohort = django_filters.CharFilter(
        method="filter_by_registration_cohort", label="Registration Cohort"
    )
    kpi_failed = django_filters.CharFilter(
        method="filter_by_kpi_failed", label="KPI Failed"
    )

    # Other filters to implement
    # All patients with learning disabilities
    # All patients with autism
    # All patients referred to CAMHS
    # All patients with generalised epilepsy
    # All patients with focal epilepsy
    # Filter by epilepsy cause
    # Filter by epilepsy syndrome

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add counts to the age range filter choices if we have a queryset
        if hasattr(self, "queryset") and self.queryset is not None:
            age_counts = CaseFilterMethods.get_age_counts(self.queryset)
            # Update age_range choices with counts
            self.form.fields["age_range"].choices = [
                ("", "---------"),  # Keep the empty choice
                ("under_12", f"Under 12 years ({age_counts['under_12']})"),
                ("12_and_over", f"12 years and over ({age_counts['12_and_over']})"),
            ]
            # Update sex choices with counts
            sex_counts = CaseFilterMethods.get_sex_counts(self.queryset)
            sex_choices = [("", "---------")]
            for code, label in SEX_TYPE:
                sex_choices.append((code, f"{label} ({sex_counts[code]})"))
            self.form.fields["sex"].choices = sex_choices

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

    def filter_by_complete_audit_progress(self, queryset, name, value):
        """Delegate to CaseFilterMethods for complete audit progress filtering"""
        return CaseFilterMethods.filter_by_complete_audit_progress(queryset, value)

    def filter_by_audit_progress_incomplete(self, queryset, name, value):
        """Delegate to CaseFilterMethods for incomplete audit progress filtering"""
        return CaseFilterMethods.filter_by_audit_progress_incomplete(queryset, value)

    def filter_by_registration_cohort(self, queryset, name, value):
        """Delegate to CaseFilterMethods for registration cohort filtering"""
        return CaseFilterMethods.filter_by_registration_cohort(queryset, value)

    def filter_by_kpi_failed(self, queryset, name, value):
        """Delegate to CaseFilterMethods for KPI failed filtering"""
        return CaseFilterMethods.filter_by_kpi_failed(queryset, value)

    class Meta:
        model = Case
        fields = [
            # simple filters for fields on the Case model
            "first_name",
            "surname",
            "nhs_number",
            "unique_reference_number",
            "sex",
            "ethnicity",
            "date_of_birth",
            "date_of_birth_range",
            "first_paediatric_assessment_date",
            # custom filters
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

    # Simple facet counts for fields on the Case model
    @staticmethod
    def get_ethnicity_counts(queryset):
        """Return counts of each ethnicity in the queryset"""
        ethnicity_counts = {}
        for code, label in ETHNICITIES:
            ethnicity_counts[code] = queryset.filter(ethnicity=code).count()
        return ethnicity_counts

    @staticmethod
    def get_sex_counts(queryset):
        """Return counts by sex"""
        sex_counts = {}
        for code, label in SEX_TYPE:
            sex_counts[code] = queryset.filter(sex=code).count()
        return sex_counts

    # Custom filter methods for filtering cases based on various criteria
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
    def filter_by_kpi_failed(queryset, value):
        """
        Filter cases by the KPI failed status.
        The string has to be split into value_type and value_id
        The value_type is "kpi" and the value_id is the KPI number.
        The KPI number is used to get the field name from the KPI_MAP dictionary.
        """
        # value_type and value_id would come from parsing the value parameter
        value_type, value_id = value.split("_", 1)

        kpi_field = KPI_MAP.get(int(value_id))

        if value_type == "kpi":
            # Filter by KPI failed status
            filter_kwargs = {f"site__organisation__kpi__{kpi_field}": 2}

            return queryset.filter(
                Q(**filter_kwargs),
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
                site__case__isnull=False,
                site__case__registration__isnull=False,
            )

        return queryset

    @staticmethod
    def get_kpi_failed_count(queryset, value):
        """
        Returns counts of case by KPI failed status - includes cases with no registration
        Accepts a value in the format of "kpi_<kpi_number>"
        The string has to be split into value_type and value_id
        The value_type is "kpi" and the value_id is the KPI number.
        The KPI number is used to get the field name from the KPI_MAP dictionary.
        """
        if not value:
            return 0
        try:
            value_type, value_id = value.split("_", 1)
        except ValueError:
            # Handle the case where value is not in the expected format
            return 0

        kpi_field = KPI_MAP.get(int(value_id))

        if value_type == "kpi":
            # Filter by KPI failed status
            filter_kwargs = {f"registration__kpi__{kpi_field}": 2}
            return (
                queryset.filter(
                    Q(**filter_kwargs),
                    site__site_is_primary_centre_of_epilepsy_care=True,
                    site__site_is_actively_involved_in_epilepsy_care=True,
                    site__case__isnull=False,
                    site__case__registration__isnull=False,
                )
                .distinct()
                .count()
            )
        return 0

    @staticmethod
    def filter_by_complete_audit_progress(queryset, value):
        """
        Filter cases by the complete audit progress status.
        Acceptable values are:
        - audit_<audit_id> for Audit
        This method assumes that the value is a string formatted as "audit_id",
        where audit_id is the ID of the audit.
        """
        # value_type and value_id would come from parsing the value parameter
        value_type, value_id = value.split("_", 1)

        if value_type == "audit":
            # Filter by complete audit progress status
            return queryset.filter(
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
                site__case__isnull=False,
                site__case__registration__isnull=False,
                registration__audit_progress__registration_complete=True,
                registration__audit_progress__first_paediatric_assessment_complete=True,
                registration__audit_progress__epilepsy_context_complete=True,
                registration__audit_progress__assessment_complete=True,
                registration__audit_progress__multiaxial_diagnosis_complete=True,
                registration__audit_progress__investigations_complete=True,
                registration__audit_progress__management_complete=True,
            )
        return queryset

    @staticmethod
    def get_complete_audit_progress_count(queryset, value):
        """
        Returns counts of case by complete audit progress status - includes cases with no registration
        Accepts a value in the format of "audit_<audit_id>"
        """
        if not value:
            return 0
        try:
            value_type, value_id = value.split("_", 1)
        except ValueError:
            # Handle the case where value is not in the expected format
            return 0

        if value_type == "audit":
            # Filter by complete audit progress status
            return (
                queryset.filter(
                    site__site_is_primary_centre_of_epilepsy_care=True,
                    site__site_is_actively_involved_in_epilepsy_care=True,
                    site__case__isnull=False,
                    site__case__registration__isnull=False,
                    registration__audit_progress__registration_complete=True,
                    registration__audit_progress__first_paediatric_assessment_complete=True,
                    registration__audit_progress__epilepsy_context_complete=True,
                    registration__audit_progress__assessment_complete=True,
                    registration__audit_progress__multiaxial_diagnosis_complete=True,
                    registration__audit_progress__investigations_complete=True,
                    registration__audit_progress__management_complete=True,
                )
                .distinct()
                .count()
            )
        return 0

    @staticmethod
    def filter_by_registration_cohort(queryset, cohort):
        """
        Filter cases by the registration cohort.
        """
        if not cohort:
            return queryset
        return queryset.filter(
            site__site_is_primary_centre_of_epilepsy_care=True,
            site__site_is_actively_involved_in_epilepsy_care=True,
            site__case__isnull=False,
            site__case__registration__isnull=False,
            registration__cohort=cohort,
        )

    @staticmethod
    def get_registration_cohort_counts(queryset, cohort):
        """
        Returns counts of case by registration cohort - includes cases with no registration
        Accepts a value in the format of "cohort_<cohort_id>"
        """
        if not cohort:
            return 0
        try:
            value_type, value_id = cohort.split("_", 1)
        except ValueError:
            # Handle the case where value is not in the expected format
            return 0

        if value_type == "cohort":
            # Filter by registration cohort
            return (
                queryset.filter(
                    site__site_is_primary_centre_of_epilepsy_care=True,
                    site__site_is_actively_involved_in_epilepsy_care=True,
                    site__case__isnull=False,
                    site__case__registration__isnull=False,
                    registration__cohort=value_id,
                )
                .distinct()
                .count()
            )
        return 0

    @staticmethod
    def filter_by_audit_progress_incomplete(queryset, value):
        """
        Filter cases by the incomplete audit progress status.
        Acceptable values are:
        - audit_<audit_id> for Audit
        This method assumes that the value is a string formatted as "audit_id",
        where audit_id is the ID of the audit.
        """
        # value_type and value_id would come from parsing the value parameter
        value_type, value_id = value.split("_", 1)

        if value_type == "audit":
            # Filter by incomplete audit progress status
            return queryset.filter(
                Q(
                    Q(registration__audit_progress__registration_complete=False)
                    | Q(
                        registration__audit_progress__first_paediatric_assessment_complete=False
                    )
                    | Q(registration__audit_progress__epilepsy_context_complete=False)
                    | Q(registration__audit_progress__assessment_complete=False)
                    | Q(
                        registration__audit_progress__multiaxial_diagnosis_complete=False
                    )
                    | Q(registration__audit_progress__investigations_complete=False)
                    | Q(registration__audit_progress__management_complete=False)
                ),
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
                site__case__isnull=False,
                site__case__registration__isnull=False,
            )
        return queryset

    @staticmethod
    def get_audit_progress_incomplete_count(queryset, value):
        """
        Returns counts of case by incomplete audit progress status - includes cases with no registration
        Accepts a value in the format of "audit_<audit_id>"
        """
        if not value:
            return 0
        try:
            value_type, value_id = value.split("_", 1)
        except ValueError:
            # Handle the case where value is not in the expected format
            return 0

        if value_type == "audit":
            # Filter by incomplete audit progress status
            return (
                queryset.filter(
                    Q(
                        Q(registration__audit_progress__registration_complete=False)
                        | Q(
                            registration__audit_progress__first_paediatric_assessment_complete=False
                        )
                        | Q(
                            registration__audit_progress__epilepsy_context_complete=False
                        )
                        | Q(registration__audit_progress__assessment_complete=False)
                        | Q(
                            registration__audit_progress__multiaxial_diagnosis_complete=False
                        )
                        | Q(registration__audit_progress__investigations_complete=False)
                        | Q(registration__audit_progress__management_complete=False)
                    ),
                    site__site_is_primary_centre_of_epilepsy_care=True,
                    site__site_is_actively_involved_in_epilepsy_care=True,
                    site__case__isnull=False,
                    site__case__registration__isnull=False,
                )
                .distinct()
                .count()
            )
        return 0

    @staticmethod
    def get_total_episodes_count(queryset, value):
        """
        Returns the total count of episodes in the queryset.
        """
        if not value:
            return 0
        try:
            value_type, value_id = value.split("_", 1)
        except ValueError:
            # Handle the case where value is not in the expected format
            return 0

        if value_type == "episodes":
            # Filter by total episodes count
            return queryset.filter(
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
            ).annotate(
                episode_count=Count(
                    "registration__multiaxialdiagnosis__episodes", distinct=True
                ).aggregate(total_episodes=Sum("episode_count"))["total_episodes"]
            )
        return 0

    @staticmethod
    def filter_episodes(queryset, value):
        """
        Filter cases by the total episodes count.
        Acceptable values are:
        - episodes_<episode_id> for Episodes
        This method assumes that the value is a string formatted as "episode_id",
        where episode_id is the ID of the episode.
        """
        # value_type and value_id would come from parsing the value parameter
        value_type, value_id = value.split("_", 1)

        if value_type == "episodes":
            # Filter by total episodes count
            return queryset.filter(
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
                registration__multiaxialdiagnosis__episodes__id=value_id,
            )
        return queryset

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
