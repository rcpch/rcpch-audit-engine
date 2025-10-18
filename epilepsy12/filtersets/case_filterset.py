from dateutil.relativedelta import relativedelta
from django.http import QueryDict
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django import forms

# Third-party imports
import django_filters
from silk.profiling.profiler import silk_profile

from ..constants import KPI_MAP, ETHNICITIES, SEX_TYPE
from epilepsy12.models import (
    Organisation,
    Case,
)


class CaseFilter(django_filters.FilterSet):
    """
    This is a FilterSet for filtering cases based on various criteria.
    Note that this is used in views that require filtering of cases, not the admin.
    It leverages the CaseFilterMethods utility class for consistent filtering logic.
    """

    # simple filters for fields on the Case model
    # Simple field filters
    search = django_filters.CharFilter(method="filter_search", label="Search")
    ethnicity = django_filters.ChoiceFilter(choices=ETHNICITIES)
    sex = django_filters.ChoiceFilter(choices=SEX_TYPE)
    index_of_multiple_deprivation_quintile = django_filters.ChoiceFilter(
        field_name="index_of_multiple_deprivation_quintile"
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
            patient_sites__site_is_actively_involved_in_epilepsy_care=True,
            patient_sites__site_is_primary_centre_of_epilepsy_care=True,
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

    country = django_filters.CharFilter(method="filter_by_country", label="Country")

    """
    Progress and Audit level filters
    """
    audit_progress_complete = django_filters.CharFilter(
        method="filter_by_audit_progress_complete", label="Complete Audit Progress"
    )

    audit_progress_incomplete = django_filters.CharFilter(
        method="filter_by_audit_progress_incomplete", label="Incomplete Audit Progress"
    )
    registration_cohort = django_filters.CharFilter(
        method="filter_by_registration_cohort", label="Registration Cohort"
    )
    kpi_failed = django_filters.BaseInFilter(
        method="filter_by_kpi_failed", label="KPI Failed"
    )
    has_support_for_mental_health_support = django_filters.CharFilter(
        method="filter_by_has_support_for_mental_health_support",
        label="Support for Mental Health",
    )
    has_been_referred_for_mental_health_support = django_filters.CharFilter(
        method="filter_by_has_been_referred_for_mental_health_support",
        label="Referred for Mental Health Support",
    )
    # Custom filter methods for filtering on related fields
    developmental_learning_or_schooling_problems = django_filters.CharFilter(
        method="filter_by_developmental_learning_or_schooling_problems",
        label="Developmental Learning or Schooling Problems",
    )
    behavioural_or_emotional_problems = django_filters.CharFilter(
        method="filter_by_behavioural_or_emotional_problems",
        label="Behavioural or Emotional Problems",
    )
    syndrome_present = django_filters.CharFilter(
        method="filter_by_syndrome_present", label="Syndrome Present"
    )
    epilepsy_cause_known = django_filters.CharFilter(
        method="filter_by_epilepsy_cause_known", label="Epilepsy Cause Known"
    )
    global_developmental_delay_or_learning_difficulties = django_filters.CharFilter(
        method="filter_by_global_developmental_delay_or_learning_difficulties",
        label="Global Developmental Delay or Learning Difficulties",
    )
    autistic_spectrum_disorder = django_filters.CharFilter(
        method="filter_by_autistic_spectrum_disorder",
        label="Autistic Spectrum Disorder",
    )
    mental_health_issue_identified = django_filters.CharFilter(
        method="filter_by_mental_health_issue_identified",
        label="Mental Health Issue Identified",
    )

    class Meta:
        model = Case
        fields = [
            # simple filters for fields on the Case model
            "nhs_number",
            "unique_reference_number",
            "first_name",
            "surname",
            "index_of_multiple_deprivation_quintile",
            "date_of_birth",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def filter_search(self, queryset, name, value):
        """
        Filter cases by the search term.
        The search term can be first name, surname, NHS number, or unique reference number, or a combination of these.
        The queryset is filtered to include only cases that match the search term.
        """
        if not value:
            return queryset

        # Split the search term into words
        search_terms = value.split()
        for term in search_terms:
            # Check if the term is a valid NHS number or unique reference number
            if term.isdigit():
                queryset = queryset.filter(
                    Q(nhs_number__icontains=term)
                    | Q(unique_reference_number__icontains=term)
                )
            else:
                # Filter by first name or surname
                queryset = queryset.filter(
                    Q(first_name__icontains=term) | Q(surname__icontains=term)
                )

        return queryset

    """
    Custom filter methods for filtering on levels of abstraction
    """

    def filter_organisation(self, queryset, name, value):
        """Delegate to CaseFilterMethods for organisation filtering"""
        return CaseFilterMethods.filter_by_organisation(queryset, value.id)

    def filter_by_trust_or_health_board(self, queryset, name, value):
        """Delegate to CaseFilterMethods for trust/health board filtering"""
        return CaseFilterMethods.filter_by_trust_or_health_board(queryset, value)

    def filter_by_integrated_care_board(self, queryset, name, value):
        """Delegate to CaseFilterMethods for ICB filtering"""
        return CaseFilterMethods.filter_by_integrated_care_board(queryset, value)

    def filter_by_nhs_england_region(self, queryset, name, value):
        """Delegate to CaseFilterMethods for NHS England region filtering"""
        return CaseFilterMethods.filter_by_nhs_england_region(queryset, value)

    def filter_by_country(self, queryset, name, value):
        """Delegate to CaseFilterMethods for country filtering"""
        return CaseFilterMethods.filter_by_country(queryset, value)

    """
    Custom filter methods for filtering on audit progress, cohort, age range and KPI
    """

    def filter_by_audit_progress_complete(self, queryset, name, value):
        """Delegate to CaseFilterMethods for complete audit progress filtering"""
        return CaseFilterMethods.filter_by_audit_progress_complete(queryset, value)

    def filter_by_audit_progress_incomplete(self, queryset, name, value):
        """Delegate to CaseFilterMethods for incomplete audit progress filtering"""
        return CaseFilterMethods.filter_by_audit_progress_incomplete(queryset, value)

    def filter_by_registration_cohort(self, queryset, name, value):
        """Delegate to CaseFilterMethods for registration cohort filtering"""
        return CaseFilterMethods.filter_by_registration_cohort(queryset, value)

    def filter_by_kpi_failed(self, queryset, name, value_list):
        """Delegate to CaseFilterMethods for KPI failed filtering"""
        if not value_list:
            return queryset
        return CaseFilterMethods.filter_by_kpi_failed(queryset, value_list)

    def filter_by_age_range(self, queryset, name, value):
        """Delegate to CaseFilterMethods for age range filtering"""
        return CaseFilterMethods.filter_by_age_range(queryset, value)

    """
    Custom filter methods for filtering on Case model fields
    """

    def filter_by_sex(self, queryset, name, value):
        """Delegate to CaseFilterMethods for sex"""
        return CaseFilterMethods.filter_by_sex(queryset, value)

    def filter_by_ethnicity(self, queryset, name, value):
        """Delegate to CaseFilterMethods for ethnicity"""
        return CaseFilterMethods.filter_by_ethnicity(queryset, value)

    def filter_by_index_of_multiple_deprivation_quintile(self, queryset, name, value):
        """Delegate to CaseFilterMethods for index of multiple deprivation quintile"""
        return CaseFilterMethods.filter_by_index_of_multiple_deprivation_quintile(
            queryset, value
        )

    """
    Custom filter methods for filtering on related fields
    """

    def filter_by_has_support_for_mental_health_support(self, queryset, name, value):
        """Delegate to CaseFilterMethods for mental health support"""
        return CaseFilterMethods.filter_by_has_support_for_mental_health_support(
            queryset, value
        )

    def filter_by_developmental_learning_or_schooling_problems(
        self, queryset, name, value
    ):
        """Delegate to CaseFilterMethods for developmental learning or schooling problems"""
        return CaseFilterMethods.filter_by_developmental_learning_or_schooling_problems(
            queryset
        )

    def filter_by_behavioural_or_emotional_problems(self, queryset, name, value):
        """Delegate to CaseFilterMethods for behavioural or emotional problems"""
        return CaseFilterMethods.filter_by_behavioural_or_emotional_problems(
            queryset, value
        )

    def filter_by_syndrome_present(self, queryset, name, value):
        """Delegate to CaseFilterMethods for syndrome presence"""
        return CaseFilterMethods.filter_by_syndrome_present(queryset, value)

    def filter_by_epilepsy_cause_known(self, queryset, name, value):
        """Delegate to CaseFilterMethods for epilepsy cause known"""
        return CaseFilterMethods.filter_by_epilepsy_cause_known(queryset, value)

    def filter_by_global_developmental_delay_or_learning_difficulties(
        self, queryset, name, value
    ):
        """Delegate to CaseFilterMethods for global developmental delay or learning difficulties"""
        return CaseFilterMethods.filter_by_global_developmental_delay_or_learning_difficulties(
            queryset, value
        )

    def filter_by_autistic_spectrum_disorder(self, queryset, name, value):
        """Delegate to CaseFilterMethods for autistic spectrum disorder"""
        return CaseFilterMethods.filter_by_autistic_spectrum_disorder(queryset, value)

    def filter_by_mental_health_issue_identified(self, queryset, name, value):
        """Delegate to CaseFilterMethods for mental health issue identified"""
        return CaseFilterMethods.filter_by_mental_health_issue_identified(
            queryset, value
        )

    def filter_by_has_been_referred_for_mental_health_support(
        self, queryset, name, value
    ):
        """Delegate to CaseFilterMethods for mental health referral status"""
        return CaseFilterMethods.filter_by_has_been_referred_for_mental_health_support(
            queryset, value
        )

    def apply_all_filters(self, queryset, request, special_filter_params=None):
        """
        Apply all filters to the queryset, including special filters
        """
        return CaseFilterMethods.apply_all_active_filters(
            queryset,
            request,
            special_filter_params=special_filter_params,
            apply_special_filters=True,
        )


class CaseFilterMethods:
    """
    This class contains custom methods for filtering cases based on various criteria.
    It is not a FilterSet itself, but rather a utility class that provides static methods
    to be used in the CaseFilter class and in the admin.
    """

    # Simple facet counts for fields on the Case model

    """
    Counts for fields on the Case model or related models
    """

    @staticmethod
    @silk_profile(name="Get Total Episodes Count")
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
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
            ).annotate(
                episode_count=Count(
                    "registration__multiaxialdiagnosis__episodes", distinct=True
                ).aggregate(total_episodes=Sum("episode_count"))["total_episodes"]
            )
        return 0

    @staticmethod
    @silk_profile(name="Get KPI Failed Counts")
    def get_kpi_failed_counts(queryset):
        """
        Returns a dictionary of KPI fields and counts of cases failing each KPI.

        Returns:
            dict: Keys are KPI numbers (1-10), values are the count of cases failing that KPI
        """

        aggregations = {}
        for key, field in KPI_MAP.items():
            if field:
                aggregations[key] = Count(
                    "id",
                    filter=Q(
                        **{f"registration__kpi__{field}": 0},
                        epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                        epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                        epilepsy12_sites__case__isnull=False,
                        epilepsy12_sites__case__registration__isnull=False,
                    ),
                )
        counts = queryset.aggregate(**aggregations)
        return {(key.strip(), KPI_MAP[key]): count for key, count in counts.items()}

    @staticmethod
    def get_all_simple_case_field_counts(queryset):
        """
        Returns a dictionary of all simple case field counts
        """
        twelve_years_ago = timezone.now().date() - relativedelta(years=12)

        aggregations = {
            # under or over 12 years
            "under_12_count": Count("id", filter=Q(date_of_birth__gt=twelve_years_ago)),
            "over_12_count": Count("id", filter=Q(date_of_birth__lte=twelve_years_ago)),
            # sex, ethnicity, index of multiple deprivation quintile
            **{f"sex_{code}": Count("id", filter=Q(sex=code)) for code, _ in SEX_TYPE},
            **{
                f"ethnicity_{code}": Count("id", filter=Q(ethnicity=code))
                for code, _ in ETHNICITIES
            },
            **{
                f"imd_{code}": Count(
                    "id", filter=Q(index_of_multiple_deprivation_quintile=code)
                )
                for code in range(1, 6)
            },
        }

        raw_counts = queryset.aggregate(**aggregations)

        # Format counts into a more usable structure
        return {
            "ethnicity_counts": {
                code: raw_counts.get(f"ethnicity_{code}", 0) for code, _ in ETHNICITIES
            },
            "sex_counts": {
                code: raw_counts.get(f"sex_{code}", 0) for code, _ in SEX_TYPE
            },
            "imd_counts": {
                code: raw_counts.get(f"imd_{code}", 0) for code in range(1, 6)
            },
            "under_12_count": raw_counts.get("under_12_count", 0),
            "over_12_count": raw_counts.get("over_12_count", 0),
        }

    @staticmethod
    def get_all_registration_related_counts(queryset):
        """
        Returns a dictionary of all registration-related counts
        Includes counts for: registration, audit progress, cohort
        """
        base_filter = Q(
            epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
            epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
            epilepsy12_sites__case__isnull=False,
        )

        aggregations = {
            # registration status
            "registered_cases": Count(
                "id", filter=base_filter & Q(registration__isnull=False), distinct=True
            ),
            "unregistered_cases": Count(
                "id", filter=base_filter & Q(registration__isnull=True), distinct=True
            ),
            # audit progress
            "audit_progress_complete": Count(
                "id",
                filter=base_filter
                & Q(registration__isnull=False)
                & Q(
                    registration__audit_progress__registration_complete=True,
                    registration__audit_progress__first_paediatric_assessment_complete=True,
                    registration__audit_progress__epilepsy_context_complete=True,
                    registration__audit_progress__assessment_complete=True,
                    registration__audit_progress__multiaxial_diagnosis_complete=True,
                    registration__audit_progress__investigations_complete=True,
                    registration__audit_progress__management_complete=True,
                ),
                distinct=True,
            ),
            "audit_progress_incomplete": Count(
                "id",
                filter=base_filter
                & Q(registration__isnull=False)
                & Q(
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
                distinct=True,
            ),
            **{
                f"cohort_{i}": Count(
                    "id",
                    filter=base_filter
                    & Q(registration__isnull=False)
                    & Q(registration__cohort=i),
                    distinct=True,
                )
                for i in range(5, 8)
            },
        }

        raw_counts = queryset.aggregate(**aggregations)

        # Format counts into a more usable structure
        return {
            "registered": raw_counts.get("registered_cases", 0),
            "unregistered": raw_counts.get("unregistered_cases", 0),
            "cases_complete": raw_counts.get("audit_progress_complete", 0),
            "cases_incomplete": raw_counts.get("audit_progress_incomplete", 0),
            "cohort_counts": {i: raw_counts.get(f"cohort_{i}", 0) for i in range(5, 8)},
        }

    @staticmethod
    def get_all_comorbidity_counts(queryset):
        """
        Returns a dictionary of all comorbidity-related counts
        Includes counts for: developmental learning or schooling problems, behavioural or emotional problems,
        syndrome present, epilepsy cause known, global developmental delay or learning difficulties,
        autistic spectrum disorder, mental health issue identified, has been referred for mental health support,
        has support for mental health support
        """

        aggregations = {
            "developmental_learning_or_schooling_problems": Count(
                "id",
                filter=Q(
                    registration__firstpaediatricassessment__developmental_learning_or_schooling_problems=True
                ),
                distinct=True,
            ),
            "behavioural_or_emotional_problems": Count(
                "id",
                filter=Q(
                    registration__firstpaediatricassessment__behavioural_or_emotional_problems=True
                ),
                distinct=True,
            ),
            "syndrome_present": Count(
                "id",
                filter=Q(registration__multiaxialdiagnosis__syndrome_present=True),
                distinct=True,
            ),
            "epilepsy_cause_known": Count(
                "id",
                filter=Q(registration__multiaxialdiagnosis__epilepsy_cause_known=True),
                distinct=True,
            ),
            "global_developmental_delay_or_learning_difficulties": Count(
                "id",
                filter=Q(
                    registration__multiaxialdiagnosis__global_developmental_delay_or_learning_difficulties=True
                ),
                distinct=True,
            ),
            "autistic_spectrum_disorder": Count(
                "id",
                filter=Q(
                    registration__multiaxialdiagnosis__autistic_spectrum_disorder=True
                ),
                distinct=True,
            ),
            "mental_health_issue_identified": Count(
                "id",
                filter=Q(
                    registration__multiaxialdiagnosis__mental_health_issue_identified=True
                ),
                distinct=True,
            ),
            "has_been_referred_for_mental_health_support": Count(
                "id",
                filter=Q(
                    registration__management__has_been_referred_for_mental_health_support=True
                ),
                distinct=True,
            ),
            "has_support_for_mental_health_support": Count(
                "id",
                filter=Q(
                    registration__management__has_support_for_mental_health_support=True
                ),
                distinct=True,
            ),
        }
        return queryset.aggregate(**aggregations)

    """
    These are methods to filter cases or related fields by various criteria
    """

    @staticmethod
    @silk_profile(name="Filter By Sex")
    def filter_by_sex(queryset, value):
        """
        Filter cases by sex
        """
        return queryset.filter(sex=value)

    @staticmethod
    @silk_profile(name="Filter By Ethnicity")
    def filter_by_ethnicity(queryset, value):
        """
        Filter by ethnicity
        """
        return queryset.filter(ethnicity=value)

    # Custom filter methods for filtering cases based on various criteria
    @staticmethod
    @silk_profile(name="Filter By Age Range")
    def filter_by_age_range(queryset, age_range):
        twelve_years_ago = timezone.now().date() - relativedelta(years=12)

        if age_range == "under_12":
            return queryset.filter(date_of_birth__gt=twelve_years_ago)
        elif age_range == "12_and_over":
            return queryset.filter(date_of_birth__lte=twelve_years_ago)
        return queryset

    @staticmethod
    def filter_by_index_of_multiple_deprivation_quintile(queryset, value):
        """
        Filter cases by index of multiple deprivation quintile
        """
        return queryset.filter(index_of_multiple_deprivation_quintile=value)

    @staticmethod
    @silk_profile(name="Filter By Registration Status")
    def filter_by_registration_status(queryset, value):
        """
        Filter cases by registration status
        """
        if value == "registered":
            return queryset.filter(
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                registration__isnull=False,
            )
        elif value == "unregistered":
            return queryset.filter(
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                registration__isnull=True,
            )
        return queryset

    @staticmethod
    @silk_profile(name="Filter By Organisation")
    def filter_by_developmental_learning_or_schooling_problems(queryset, value=None):
        """
        Filter cases by developmental learning or schooling problems
        """
        return queryset.filter(
            registration__firstpaediatricassessment__developmental_learning_or_schooling_problems=True
        )

    @staticmethod
    @silk_profile(name="Filter By Behavioural or Emotional Problems")
    def filter_by_behavioural_or_emotional_problems(queryset, value=None):
        """
        Filter cases by behavioural or emotional problems
        """
        return queryset.filter(
            registration__firstpaediatricassessment__behavioural_or_emotional_problems=True
        )

    @staticmethod
    @silk_profile(name="Filter By Syndrome Present")
    def filter_by_syndrome_present(queryset, value=None):
        """
        Filter cases by syndrome presence
        """
        return queryset.filter(registration__multiaxialdiagnosis__syndrome_present=True)

    @staticmethod
    @silk_profile(name="Filter By Epilepsy Cause Known")
    def filter_by_epilepsy_cause_known(queryset, value=None):
        """
        Filter cases where epilepsy cause is known
        """
        return queryset.filter(
            registration__multiaxialdiagnosis__epilepsy_cause_known=True
        )

    @staticmethod
    @silk_profile(name="Filter By Global Developmental Delay or Learning Difficulties")
    def filter_by_global_developmental_delay_or_learning_difficulties(
        queryset, value=None
    ):
        """
        Filter cases with global developmental delay or learning difficulties
        """
        return queryset.filter(
            registration__multiaxialdiagnosis__global_developmental_delay_or_learning_difficulties=True
        )

    @staticmethod
    @silk_profile(name="Filter By Autistic Spectrum Disorder")
    def filter_by_autistic_spectrum_disorder(queryset, value=None):
        """
        Filter cases with autistic spectrum disorder
        """
        return queryset.filter(
            registration__multiaxialdiagnosis__autistic_spectrum_disorder=True
        )

    @staticmethod
    @silk_profile(name="Filter By Mental Health Issue Identified")
    def filter_by_mental_health_issue_identified(queryset, value=None):
        """
        Filter cases with identified mental health issues
        """
        return queryset.filter(
            registration__multiaxialdiagnosis__mental_health_issue_identified=True
        )

    @staticmethod
    @silk_profile(name="Filter By Has Been Referred For Mental Health Support")
    def filter_by_has_been_referred_for_mental_health_support(queryset, value=None):
        """
        Filter cases where patient has been referred for mental health support
        """
        return queryset.filter(
            registration__management__has_been_referred_for_mental_health_support=True
        )

    @staticmethod
    @silk_profile(name="Filter By Has Support For Mental Health Support")
    def filter_by_has_support_for_mental_health_support(queryset, value=None):
        """
        Filter cases where patient has mental health support in place
        """
        if not value:
            return queryset

        return queryset.filter(
            registration__management__has_support_for_mental_health_support=True
        )

    """
    Methods to filter cases by organisation, trust, health board, integrated care board,
    """

    @staticmethod
    @silk_profile(name="Filter By Organisation")
    def filter_by_organisation(queryset, organisation_id):
        if not organisation_id:
            return queryset
        return queryset.filter(
            epilepsy12_sites__organisation_id=organisation_id,
            epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
            epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
        )

    @staticmethod
    @silk_profile(name="Filter By Trust or Local Health Board")
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
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                epilepsy12_sites__case__isnull=False,
                epilepsy12_sites__case__registration__isnull=False,
                epilepsy12_sites__organisation__trust__id=value_id,
            )
        elif value_type == "h":
            # Filter by Local Health Board
            return queryset.filter(
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                epilepsy12_sites__case__isnull=False,
                epilepsy12_sites__case__registration__isnull=False,
                epilepsy12_sites__organisation__local_health_board__id=value_id,
            )
        return queryset

    @staticmethod
    @silk_profile(name="Filter By Integrated Care Board")
    def filter_by_integrated_care_board(queryset, value):
        """
        Filter cases by the integrated care board their site is part of.
        """
        value_type, value_id = value.split("_", 1)

        if value_type == "icb":
            # Filter by Integrated Care Board
            return queryset.filter(
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                epilepsy12_sites__case__isnull=False,
                epilepsy12_sites__case__registration__isnull=False,
                epilepsy12_sites__organisation__integrated_care_board__id=value_id,
            )
        return queryset

    @staticmethod
    @silk_profile(name="Filter By NHS England Region")
    def filter_by_nhs_england_region(queryset, value):
        """
        Filter cases by the NHS England region their site is part of.
        """
        value_type, value_id = value.split("_", 1)

        if value_type == "nhsenglandregion":
            # Filter by NHS England Region
            return queryset.filter(
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                epilepsy12_sites__case__isnull=False,
                epilepsy12_sites__case__registration__isnull=False,
                epilepsy12_sites__organisation__nhs_england_region__id=value_id,
            )
        return queryset

    @staticmethod
    @silk_profile(name="Filter By Country")
    def filter_by_country(queryset, value):
        """
        Filter cases by the country their site is part of.
        """
        # value_type and value_id would come from parsing the value parameter
        value_type, value_id = value.split("_", 1)

        if value_type == "country":
            # Filter by Country
            return queryset.filter(
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                epilepsy12_sites__case__isnull=False,
                epilepsy12_sites__case__registration__isnull=False,
                epilepsy12_sites__organisation__country__id=value_id,
            )
        return queryset

    """
    Methods to get all trusts, local health boards, integrated care boards, NHS England regions, and countries for the dropdowns
    The lists filter out any trusts or health boards that are not part of a site that is a primary centre of epilepsy care or there are no patients
    """

    @staticmethod
    @silk_profile(name="Get All Trusts and Local Health Boards")
    def all_trusts_and_local_health_boards(queryset):
        """
        Returns all trusts and local health boards in One queryset.
        This method assumes that the queryset is already filtered to include only cases
        that are part of a site that is a primary centre of epilepsy care and is actively involved in epilepsy care.
        Acceptable values are:
        - t_<trust_id> for Trust
        - h_<health_board_id> for Health Board
        """
        trusts = (
            queryset.filter(
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                epilepsy12_sites__case__isnull=False,
            )
            .values(
                "epilepsy12_sites__organisation__trust__id",
                "epilepsy12_sites__organisation__trust__name",
            )
            .annotate(count=Count("id", distinct=True))
            .order_by("epilepsy12_sites__organisation__trust__name")
        )

        # Get health boards with active registered cases
        local_health_boards = (
            queryset.filter(
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                epilepsy12_sites__case__isnull=False,
                epilepsy12_sites__case__registration__isnull=False,
            )
            .values(
                "epilepsy12_sites__organisation__local_health_board__id",
                "epilepsy12_sites__organisation__local_health_board__name",
            )
            .annotate(count=Count("id", distinct=True))
            .order_by("epilepsy12_sites__organisation__local_health_board__name")
        )

        result = []
        # Get counts for trusts
        for trust in trusts:
            result.append(
                (
                    f"t_{trust['epilepsy12_sites__organisation__trust__id']}",
                    f"Trust: {trust['epilepsy12_sites__organisation__trust__name']} ({trust['count']})",
                )
            )
        # Get counts for health boards
        for hb in local_health_boards:
            result.append(
                (
                    f"h_{hb['epilepsy12_sites__organisation__local_health_board__id']}",
                    f"Local Health Board: {hb['epilepsy12_sites__organisation__local_health_board__name']} ({hb['count']})",
                )
            )

        return result

    @staticmethod
    @silk_profile(name="Get All Integrated Care Boards")
    def all_integrated_care_boards(queryset):
        """
        Returns all integrated care boards in the queryset.
        This method assumes that the queryset is already filtered to include only cases
        that are part of a site that is a primary centre of epilepsy care and is actively involved in epilepsy care.
        """
        integrated_care_boards = (
            queryset.filter(
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                epilepsy12_sites__case__isnull=False,
            )
            .values(
                "epilepsy12_sites__organisation__integrated_care_board__id",
                "epilepsy12_sites__organisation__integrated_care_board__name",
            )
            .annotate(count=Count("id", distinct=True))
            .order_by("epilepsy12_sites__organisation__integrated_care_board__name")
        )

        return [
            (
                f"icb_{icb['epilepsy12_sites__organisation__integrated_care_board__id']}",
                f"{icb['epilepsy12_sites__organisation__integrated_care_board__name']} ({icb['count']})",
            )
            for icb in integrated_care_boards
        ]

    @staticmethod
    @silk_profile(name="Get All NHS England Regions")
    def all_nhs_england_regions(queryset):
        """
        Returns all NHS England regions in the queryset.
        """
        regions = (
            queryset.filter(
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                epilepsy12_sites__case__isnull=False,
            )
            .values(
                "epilepsy12_sites__organisation__nhs_england_region__id",
                "epilepsy12_sites__organisation__nhs_england_region__name",
            )
            .annotate(count=Count("id", distinct=True))
            .order_by("epilepsy12_sites__organisation__nhs_england_region__name")
        )

        return [
            (
                f"nhsenglandregion_{region['epilepsy12_sites__organisation__nhs_england_region__id']}",
                f"{region['epilepsy12_sites__organisation__nhs_england_region__name']} ({region['count']})",
            )
            for region in regions
        ]

    @staticmethod
    @silk_profile(name="Get All Countries")
    def all_countries(queryset):
        countries = (
            queryset.filter(
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                epilepsy12_sites__case__isnull=False,
            )
            .values(
                "epilepsy12_sites__organisation__country__id",
                "epilepsy12_sites__organisation__country__name",
            )
            .annotate(count=Count("id", distinct=True))
            .order_by("epilepsy12_sites__organisation__country__name")
        )
        # Get counts for countries

        return [
            (
                f"country_{country['epilepsy12_sites__organisation__country__id']}",
                f"{country['epilepsy12_sites__organisation__country__name']} ({country['count']})",
            )
            for country in countries
        ]

    """
    Methods to filter cases by KPI failed status / Audit progress status / Cohort / Episodes
    """

    @staticmethod
    @silk_profile(name="Filter By KPI Failed")
    def filter_by_kpi_failed(queryset, value_list):
        """
        Filter cases by the KPI failed status. Differs from other filters as accepts a list of kpis
        """

        kpi_fields = [
            KPI_MAP[key] for key in value_list if key in KPI_MAP
        ]  # converts the list of kpi keys to the corresponding field names
        if not kpi_fields:
            # If no matching KPI fields are found, return the original queryset
            return queryset

        filter_kwargs = Q()
        for kpi_field in kpi_fields:
            filter_kwargs &= Q(**{f"registration__kpi__{kpi_field}": 0})

        # Filter by KPI failed status

        return queryset.filter(
            filter_kwargs,
            epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
            epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
            epilepsy12_sites__case__isnull=False,
            epilepsy12_sites__case__registration__isnull=False,
        )

    @staticmethod
    def filter_by_audit_progress_complete(queryset, value):
        """
        Filter cases by the complete audit progress status.
        Accepts a boolean value
        """
        # value_type and value_id would come from parsing the value parameter
        if value:
            # Filter by complete audit progress status
            return queryset.filter(
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                epilepsy12_sites__case__isnull=False,
                epilepsy12_sites__case__registration__isnull=False,
                registration__audit_progress__registration_complete=True,
                registration__audit_progress__first_paediatric_assessment_complete=True,
                registration__audit_progress__epilepsy_context_complete=True,
                registration__audit_progress__assessment_complete=True,
                registration__audit_progress__multiaxial_diagnosis_complete=True,
                registration__audit_progress__investigations_complete=True,
                registration__audit_progress__management_complete=True,
            )
        else:
            return queryset

    @staticmethod
    @silk_profile(name="Filter By Registration Cohort")
    def filter_by_registration_cohort(queryset, cohort):
        """
        Filter cases by the registration cohort.
        """
        if not cohort:
            return queryset
        return queryset.filter(
            epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
            epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
            epilepsy12_sites__case__isnull=False,
            epilepsy12_sites__case__registration__isnull=False,
            registration__cohort=cohort,
        )

    @staticmethod
    @silk_profile(name="Filter By Audit Progress Incomplete")
    def filter_by_audit_progress_incomplete(queryset, value):
        """
        Filter cases by the incomplete audit progress status.
        Acceptable values are:
        boolean value
        """
        # value_type and value_id would come from parsing the value parameter
        if value:
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
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                epilepsy12_sites__case__isnull=False,
                epilepsy12_sites__case__registration__isnull=False,
            )
        return queryset

    @staticmethod
    @silk_profile(name="Filter Episodes")
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
                epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
                registration__multiaxialdiagnosis__episodes__id=value_id,
            )
        return queryset

    """
    This final method is used to add all the filters to the filterset.
    """

    @staticmethod
    @silk_profile(name="Apply All Active Case Filters")
    def apply_all_active_filters(
        queryset,
        request,
        exclude_params=None,
        special_filter_params=None,
        apply_special_filters=False,
    ):
        """
        Apply all filters from request - both standard and special filters if needed
        """
        # Initialize empty lists if None
        if type(exclude_params) is not list:
            exclude_params = [exclude_params] if exclude_params else []
        else:
            exclude_params = exclude_params if exclude_params else []

        if type(special_filter_params) is not list:
            special_filter_params = (
                [special_filter_params] if special_filter_params else []
            )
        else:
            special_filter_params = (
                special_filter_params if special_filter_params else []
            )

        # Always exclude pagination parameter - handle both 'p' and 'page'
        if "p" not in exclude_params:
            exclude_params.append("p")
        if "page" not in exclude_params:
            exclude_params.append("page")

        # First apply any special filters if requested
        if apply_special_filters:
            # These take no extra values and only filter by the value of the parameter
            # Includes:
            # "audit_progress_complete",
            # "audit_progress_incomplete",
            # "registration_cohort",

            # # level of abstraction fields:
            # "trust_or_health_board",
            # "integrated_care_board",
            # "nhs_england_region",
            # "country",

            # # related fields
            # "developmental_learning_or_schooling_problems"
            # "behavioural_or_emotional_problems"
            # "syndrome_present"
            # "epilepsy_cause_known"
            # "global_developmental_delay_or_learning_difficulties"
            # "autistic_spectrum_disorder"
            # "mental_health_issue_identified"
            # "has_been_referred_for_mental_health_support"
            # "has_support_for_mental_health_support"

            for param_name in special_filter_params:
                if param_name in request.GET and request.GET[param_name]:
                    # Call the appropriate filter method based on parameter name
                    filter_value = request.GET[param_name]
                    if filter_value == "true":
                        filter_value = True
                    elif filter_value == "false":
                        filter_value = False
                    else:
                        filter_value = request.GET[param_name]

                    filter_method = getattr(
                        CaseFilterMethods, f"filter_by_{param_name}", None
                    )

                    if filter_method:
                        # Apply the filter
                        queryset = filter_method(queryset, filter_value)

        # Then handle all remaining filters
        for key, value in request.GET.items():
            # Skip excluded params, empty values, and special params if they were already applied
            if (
                key in exclude_params
                or not value
                or (apply_special_filters and key in special_filter_params)
            ):
                continue

            # Apply standard filters through explicit cases
            if key == "organisation":
                queryset = CaseFilterMethods.filter_by_organisation(
                    queryset=queryset, organisation_id=value
                )
            elif key == "sex":
                queryset = CaseFilterMethods.filter_by_sex(
                    queryset=queryset, value=value
                )
            elif key == "age_range":
                queryset = CaseFilterMethods.filter_by_age_range(
                    queryset=queryset, age_range=value
                )
            elif key == "registration_status":
                queryset = CaseFilterMethods.filter_by_registration_status(
                    queryset=queryset, value=value
                )
            elif key == "kpi_failed":
                # This is a special case where we need to handle the KPI failed status for a list of KPIs as a single query
                value_list = request.GET.getlist(key)
                queryset = CaseFilterMethods.filter_by_kpi_failed(
                    queryset=queryset, value_list=value_list
                )
            elif key == "index_of_multiple_deprivation_quintile":
                queryset = (
                    CaseFilterMethods.filter_by_index_of_multiple_deprivation_quintile(
                        queryset=queryset, value=value
                    )
                )
        return queryset
