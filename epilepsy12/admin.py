from typing import Any

# Django
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
from django.db.models import Count, Prefetch
from django.forms import forms


# Third-party
from epilepsy12.models_folder.audit_period import AuditPeriodExtension
from simple_history.admin import SimpleHistoryAdmin


from .models import *
from .organisational_audit import export_submission_period_as_csv
from .filtersets import *

"""
Facets and filters for the Epilepsy12 admin site
"""


class OrganisationCaseFilter(admin.SimpleListFilter):
    title = "Organisation"
    parameter_name = "organisation"

    def lookups(self, request, model_admin):
        """
        Returns a list of Organisations for the dropdown filter.
        The list only contains organisations that are actively involved in epilepsy care.
        """
        organisations = (
            Organisation.objects.filter(
                patient_sites__site_is_actively_involved_in_epilepsy_care=True,
                patient_sites__site_is_primary_centre_of_epilepsy_care=True,
                patient_sites__organisation__isnull=False,
                patient_sites__case__isnull=False,
                patient_sites__case__registration__isnull=False,
            )
            .annotate(case_count=Count("patient_sites__case", distinct=True))
            .distinct()
            .order_by("name")
        )  # populates the dropdown with organisations

        # Get the base queryset for counting
        base_queryset = model_admin.get_queryset(request)
        # Apply all active filters to the base queryset
        # to get the counts for each organisation
        filtered_queryset = CaseFilterMethods.apply_all_active_filters(
            base_queryset, request, exclude_params=self.parameter_name
        )

        return [
            (
                org.pk,
                f"{org.name} ({org.case_count})",
            )
            for org in organisations
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        # Filter by organisation
        organisation_id = self.value()

        # If this is a Case admin view, filter by cases that have this organisation as their primary centre
        if queryset.model == Case:
            return CaseFilterMethods.filter_by_organisation(
                queryset=queryset, organisation_id=organisation_id
            )

        # If this is for another model that has a direct relation to organisation
        elif hasattr(queryset.model, "organisation"):
            return queryset.filter(organisation_id=organisation_id)

        # For models related to Case, such as Registration, MultiaxialDiagnosis, etc.
        elif hasattr(queryset.model, "case"):
            return queryset.filter(
                case__epilepsy12_sites__organisation_id=organisation_id,
                case__epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                case__epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
            )

        # Handle Registration model
        elif queryset.model == Registration:
            return queryset.filter(
                case__epilepsy12_sites__organisation_id=organisation_id,
                case__epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True,
                case__epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True,
            ).distinct()

        # Default fallback for other models
        return queryset


class TrustOrLocalHealthBoardFilter(admin.SimpleListFilter):
    title = "Trust or Local Health Board"
    parameter_name = "trust_or_local_health_board"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples for the dropdown filter.
        The list only contains trusts and health boards that are actively involved in epilepsy care.
        """
        trusts = (
            Trust.objects.filter(
                organisation__patient_sites__site_is_primary_centre_of_epilepsy_care=True,
                organisation__patient_sites__site_is_actively_involved_in_epilepsy_care=True,
                organisation__patient_sites__case__isnull=False,
            )
            .distinct()
            .order_by("name")
        )

        # Get health boards with active registered cases
        local_health_boards = (
            LocalHealthBoard.objects.filter(
                organisation__patient_sites__site_is_primary_centre_of_epilepsy_care=True,
                organisation__patient_sites__site_is_actively_involved_in_epilepsy_care=True,
                organisation__patient_sites__case__isnull=False,
                organisation__patient_sites__case__registration__isnull=False,
            )
            .distinct()
            .order_by("name")
        )

        # Get the base queryset for counting
        base_queryset = model_admin.get_queryset(request)
        # Apply all active filters to the base queryset
        # to get the counts for each trust and health board
        filtered_queryset = CaseFilterMethods.apply_all_active_filters(
            base_queryset, request, exclude_params=self.parameter_name
        )
        result = []
        # Get counts for trusts
        for trust in trusts:
            trust_filtered = CaseFilterMethods.filter_by_trust_or_health_board(
                queryset=filtered_queryset, value=f"t_{trust.id}"
            )
            trust_counts = (
                trust_filtered.count()
                if hasattr(trust_filtered, "count")
                else trust_filtered
            )
            result.append((f"t_{trust.id}", f"Trust: {trust.name} ({trust_counts})"))
        # Get counts for health boards
        for hb in local_health_boards:
            local_health_board_filtered = (
                CaseFilterMethods.filter_by_trust_or_health_board(
                    queryset=filtered_queryset, value=f"h_{hb.id}"
                )
            )
            local_health_board_counts = (
                local_health_board_filtered.count()
                if hasattr(local_health_board_filtered, "count")
                else local_health_board_filtered
            )
            result.append(
                (f"h_{hb.id}", f"Health Board: {hb.name} ({local_health_board_counts})")
            )

        return result

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        return CaseFilterMethods.filter_by_trust_or_health_board(
            queryset=queryset, value=self.value()
        )


class IntegratedCareBoardFilter(admin.SimpleListFilter):
    title = "Integrated Care Board"
    parameter_name = "integrated_care_board"

    def lookups(self, request, model_admin):
        """
        Returns a list of Integrated Care Boards for the dropdown filter.
        The list only contains integrated care boards that are actively involved in epilepsy care.
        """
        icbs = (
            IntegratedCareBoard.objects.filter(
                organisation__patient_sites__site_is_primary_centre_of_epilepsy_care=True,
                organisation__patient_sites__site_is_actively_involved_in_epilepsy_care=True,
                organisation__patient_sites__case__isnull=False,
            )
            .distinct()
            .order_by("name")
        )

        # Get the base queryset for counting
        base_queryset = model_admin.get_queryset(request)
        # Apply all active filters to the base queryset
        # to get the counts for each integrated care board
        filtered_queryset = CaseFilterMethods.apply_all_active_filters(
            base_queryset, request, exclude_params=self.parameter_name
        )

        return [
            (
                f"i_{icb.id}",
                f"{icb.name} ({CaseFilterMethods.filter_by_integrated_care_board(queryset=filtered_queryset, value=f'i_{icb.id}').count()})",
            )
            for icb in icbs
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        return CaseFilterMethods.filter_by_integrated_care_board(
            queryset=queryset, value=self.value()
        )


class NHSEnglandRegionFilter(admin.SimpleListFilter):
    title = "NHS England Region"
    parameter_name = "nhs_england_region"

    def lookups(self, request, model_admin):
        """
        Returns a list of NHS England Regions for the dropdown filter.
        The list only contains NHS England regions that are actively involved in epilepsy care.
        """
        regions = (
            NHSEnglandRegion.objects.filter(
                organisation__patient_sites__site_is_primary_centre_of_epilepsy_care=True,
                organisation__patient_sites__site_is_actively_involved_in_epilepsy_care=True,
                organisation__patient_sites__case__isnull=False,
            )
            .distinct()
            .order_by("name")
        )
        # Get the base queryset for counting
        base_queryset = model_admin.get_queryset(request)
        # Apply all active filters to the base queryset
        # to get the counts for each NHS England region
        filtered_queryset = CaseFilterMethods.apply_all_active_filters(
            base_queryset, request, exclude_params=self.parameter_name
        )
        # Get counts for NHS England regions

        return [
            (
                f"nhs_{region.id}",
                f"{region.name} ({CaseFilterMethods.filter_by_nhs_england_region(queryset=filtered_queryset, value=f'nhs_{region.id}').count()})",
            )
            for region in regions
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        return CaseFilterMethods.filter_by_nhs_england_region(
            queryset=queryset, value=self.value()
        )


class CountryFilter(admin.SimpleListFilter):
    title = "Country"
    parameter_name = "country"

    def lookups(self, request, model_admin):
        """
        Returns a list of countries for the dropdown filter.
        The list only contains countries that are actively involved in epilepsy care.
        """
        countries = (
            Country.objects.filter(
                organisation__patient_sites__site_is_primary_centre_of_epilepsy_care=True,
                organisation__patient_sites__site_is_actively_involved_in_epilepsy_care=True,
                organisation__patient_sites__case__isnull=False,
            )
            .distinct()
            .order_by("name")
        )
        # Get the base queryset for counting
        base_queryset = model_admin.get_queryset(request)
        # Apply all active filters to the base queryset
        # to get the counts for each country
        filtered_queryset = CaseFilterMethods.apply_all_active_filters(
            base_queryset, request, exclude_params=self.parameter_name
        )
        # Get counts for countries

        return [
            (
                f"c_{country.id}",
                f"{country.name} ({CaseFilterMethods.filter_by_country(queryset=filtered_queryset, value=f'c_{country.id}').count()})",
            )
            for country in countries
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        return CaseFilterMethods.filter_by_country(
            queryset=queryset, value=self.value()
        )


class AgeRangeFilter(admin.SimpleListFilter):
    title = "Age Range"
    parameter_name = "age_range"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples for the dropdown filter.
        The list contains two options: "Under 12 years" and "12 years and over",
        as well as the total counts of each.
        """
        base_queryset = model_admin.get_queryset(request)
        filtered_queryset = CaseFilterMethods.apply_all_active_filters(
            base_queryset, request, exclude_params=self.parameter_name
        )
        # Get counts for age ranges
        counts = CaseFilterMethods.get_all_simple_case_field_counts(
            queryset=filtered_queryset
        )

        return [
            ("under_12", f"Under 12 years ({counts['under_12_count']})"),
            ("12_and_over", f"12 years and over ({counts['over_12_count']})"),
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        return CaseFilterMethods.filter_by_age_range(
            queryset=queryset, age_range=self.value()
        )


"""
Admin customisation for Epilepsy12 models
"""


class Epilepsy12UserAdmin(UserAdmin, SimpleHistoryAdmin):

    def get_employer_organisations(self, obj):
        if obj:
            return ", ".join(
                [
                    (
                        str(org.employer_organisation) + " (Primary)"
                        if org.is_primary
                        else str(org.employer_organisation)
                    )
                    for org in obj.employer_organisations.all()
                ]
            )
        return ""

    get_employer_organisations.short_description = "Employer Organisations"

    ordering = ["email"]
    model = Epilepsy12User
    list_display = [
        "email",
        "first_name",
        "surname",
        "is_active",
        "is_staff",
        "is_rcpch_staff",
        "is_rcpch_audit_team_member",
        "role",
        "get_employer_organisations",
    ]
    search_fields = (
        "email",
        "surname",
        "role",
        "is_active",
    )
    list_filter = (
        "is_active",
        "role",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "first_name",
                    "surname",
                )
            },
        ),
        ("Contacts", {"fields": ("email",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_rcpch_staff",
                    "is_rcpch_audit_team_member",
                    "is_superuser",
                    "email_confirmed",
                    "view_preference",
                )
            },
        ),
        (
            "Access",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "password_last_set",
                )
            },
        ),
        (
            "Group Permissions",
            {
                "classes": ("collapse",),
                "fields": (
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "title",
                    "first_name",
                    "surname",
                    "is_staff",
                    "is_rcpch_staff",
                    "is_active",
                    "is_rcpch_audit_team_member",
                    "role",
                    "is_superuser",
                    "groups",
                ),
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            self.exclude = ["is_superuser"]
        else:
            self.exclude = []
        if request.user.groups.filter(name="trust_audit_team_edit_access"):
            form.base_fields["groups"].disabled = True
            form.base_fields["first_name"].disabled = True
            form.base_fields["surname"].disabled = True
            form.base_fields["title"].disabled = True
            form.base_fields["email"].disabled = True
            form.base_fields["is_staff"].disabled = True
            form.base_fields["is_rcpch_staff"].disabled = True
            form.base_fields["is_rcpch_audit_team_member"].disabled = True
        return form


class CaseAdmin(SimpleHistoryAdmin):
    def get_registration(self, obj):
        if obj.registration:
            return f"{obj.registration.first_paediatric_assessment_date}"
        return "Unregistered"

    def get_unique_identifier(self, obj):
        if obj.nhs_number:
            return f"{obj.nhs_number}"
        elif obj.unique_reference_number:
            return f"{obj.unique_reference_number}"
        else:
            return "No Unique Identifier"

    def get_e12_id(self, obj):
        if obj.registration:
            return f"{obj.registration.pk}"
        return "No E12 ID"

    def get_lead_e12_site(self, obj):
        site = Site.objects.filter(
            site_is_primary_centre_of_epilepsy_care=True,
            site_is_actively_involved_in_epilepsy_care=True,
            case=obj,
        ).get()
        if site:
            if site.organisation.country.boundary_identifier == "W92000004":
                return (
                    f"{site.organisation.name} ({site.organisation.local_health_board})"
                )
            else:
                return f"{site.organisation.name} ({site.organisation.trust})"

    def episode_count_display(self, obj):
        """Display the episode count in the admin list"""
        return obj.episode_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return (
            queryset.annotate(
                episode_count=Count("registration__multiaxialdiagnosis__episodes")
            )
            .select_related("registration")
            .prefetch_related(
                Prefetch(
                    "registration__multiaxialdiagnosis",
                    queryset=MultiaxialDiagnosis.objects.prefetch_related("episodes"),
                )
            )
        )

    get_registration.short_description = "First Paediatric Assessment"
    get_e12_id.short_description = "E12 ID"
    get_unique_identifier.short_description = "Unique Identifier"
    get_lead_e12_site.short_description = "Lead E12 Site"
    episode_count_display.short_description = "Seizure Episodes"

    ordering = ["surname"]
    search_fields = [
        "first_name",
        "surname",
        "nhs_number",
        "unique_reference_number",
        "date_of_birth",
    ]

    list_filter = [
        AgeRangeFilter,
        "registration__audit_period__cohort_number",
        OrganisationCaseFilter,
        TrustOrLocalHealthBoardFilter,
        IntegratedCareBoardFilter,
        NHSEnglandRegionFilter,
        CountryFilter,
    ]

    list_display = [
        "get_e12_id",
        "first_name",
        "surname",
        "get_unique_identifier",
        "date_of_birth",
        "age",
        "get_registration",
        "get_lead_e12_site",
        "episode_count_display",
    ]

    list_select_related = ["registration__audit_period"]


class OrganisationalAuditSubmissionAdmin(SimpleHistoryAdmin):
    search_fields = [
        "trust__name",
        "local_health_board__name",
        "trust__ods_code",
        "local_health_board__ods_code",
    ]
    list_filter = ["submission_period"]


class OrganisationalAuditSubmissionPeriodAdmin(SimpleHistoryAdmin):
    actions = ["download"]

    @admin.action(description="Download submissions as CSV")
    def download(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(
                request,
                "Please select only one submission period to download",
                messages.ERROR,
            )
        else:
            submission_period = queryset.first()

            filename = f"e12-org-audit-{submission_period.year}.csv"

            data = export_submission_period_as_csv(submission_period)

            response = HttpResponse(data, content_type="text/csv")
            response["Content-Disposition"] = f"attachment; filename={filename}"

            return response


class OrganisationAdmin(SimpleHistoryAdmin):
    search_fields = ["name", "ods_code"]
    list_display = ["name", "ods_code", "trust", "local_health_board", "country"]
    list_filter = ["country", "nhs_england_region", "trust", "local_health_board"]


class OrganisationEmployerAdmin(SimpleHistoryAdmin):
    model = OrganisationEmployer

    list_display = [
        "epilepsy12_user",
        "employer_organisation",
        "is_primary",
        "is_active",
        "date_joined",
    ]
    list_filter = [
        "is_active",
        "is_primary",
        "employer_organisation",
    ]
    search_fields = [
        "epilepsy12_user__email",
        "epilepsy12_user__first_name",
        "epilepsy12_user__surname",
        "employer_organisation__name",
    ]


class TrustAdmin(SimpleHistoryAdmin):
    search_fields = ["name", "ods_code"]


class AuditPeriodAdmin(SimpleHistoryAdmin):
    list_display = ["cohort_number", "name", "slug", "recruitment_start_date", "recruitment_end_date", "data_collection_end_date", "submission_deadline"]
    ordering = ["-recruitment_start_date"]
    readonly_fields = ["slug"]

class AuditPeriodExtensionAdmin(SimpleHistoryAdmin):
    list_display = ["audit_period", "organisation", "extended_submission_date"]
    list_filter = ["audit_period"]
    autocomplete_fields = ["organisation"]
    list_select_related = ["organisation", "audit_period"]

# register all models
admin.site.register(Epilepsy12User, Epilepsy12UserAdmin)
admin.site.register(AntiEpilepsyMedicine, SimpleHistoryAdmin)
admin.site.register(Assessment, SimpleHistoryAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(Comorbidity, SimpleHistoryAdmin)
admin.site.register(EpilepsyContext, SimpleHistoryAdmin)
admin.site.register(Investigations, SimpleHistoryAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(OrganisationEmployer, OrganisationEmployerAdmin)


admin.site.register(FirstPaediatricAssessment, SimpleHistoryAdmin)
admin.site.register(Management, SimpleHistoryAdmin)
admin.site.register(Registration, SimpleHistoryAdmin)
admin.site.register(Site, SimpleHistoryAdmin)
admin.site.register(AuditPeriod, AuditPeriodAdmin)
admin.site.register(AuditPeriodExtension, AuditPeriodExtensionAdmin)
admin.site.register(AuditProgress, SimpleHistoryAdmin)
admin.site.register(Episode, SimpleHistoryAdmin)

admin.site.register(Keyword, SimpleHistoryAdmin)
admin.site.register(MultiaxialDiagnosis, SimpleHistoryAdmin)
admin.site.register(SyndromeList, SimpleHistoryAdmin)
admin.site.register(Syndrome, SimpleHistoryAdmin)
admin.site.register(EpilepsyCause, SimpleHistoryAdmin)
admin.site.register(KPI)

admin.site.register(OrganisationKPIAggregation)
admin.site.register(TrustKPIAggregation)
admin.site.register(LocalHealthBoardKPIAggregation)
admin.site.register(ICBKPIAggregation)
admin.site.register(NHSEnglandRegionKPIAggregation)
admin.site.register(OpenUKKPIAggregation)
admin.site.register(CountryKPIAggregation)
admin.site.register(NationalKPIAggregation)

admin.site.register(VisitActivity)
admin.site.register(ComorbidityList)
admin.site.register(Medicine)

admin.site.register(Country)
admin.site.register(LondonBorough)
admin.site.register(IntegratedCareBoard)
admin.site.register(NHSEnglandRegion)

admin.site.register(Trust, TrustAdmin)
admin.site.register(LocalHealthBoard)
admin.site.register(OPENUKNetwork)

admin.site.register(OrganisationalAuditSubmission, OrganisationalAuditSubmissionAdmin)
admin.site.register(
    OrganisationalAuditSubmissionPeriod, OrganisationalAuditSubmissionPeriodAdmin
)
admin.site.register(Banner)


# Customise the admin site
admin.site.site_header = "Epilepsy12 admin"
admin.site.site_title = "Epilepsy12 admin"
admin.site.index_title = "Epilepsy12"
admin.site.site_url = "/"
