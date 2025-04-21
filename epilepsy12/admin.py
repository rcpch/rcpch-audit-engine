from typing import Any

# Django
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
from django.db.models import Count, Prefetch

# Third-party
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.
from .models import *
from .organisational_audit import export_submission_period_as_csv


"""
Facets and filters for the Epilepsy12 admin site
"""


class OrganisationFilter(admin.SimpleListFilter):
    title = "Organisation"
    parameter_name = "organisation"

    def lookups(self, request, model_admin):
        organisations = (
            Organisation.objects.filter(
                site__site_is_actively_involved_in_epilepsy_care=True,
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__organisation__isnull=False,
            )
            .distinct()
            .order_by("name")
        )  # populates the dropdown with organisations
        return [(org.pk, org.name) for org in organisations]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(organisation__pk=self.value())
        return queryset


class TrustOrLocalHealthBoardFilter(admin.SimpleListFilter):
    title = "Trust or Local Health Board"
    parameter_name = "trust_or_local_health_board"

    def lookups(self, request, model_admin):
        trusts = (
            Trust.objects.filter(
                organisation__site__site_is_primary_centre_of_epilepsy_care=True,
                organisation__site__site_is_actively_involved_in_epilepsy_care=True,
                organisation__site__case__isnull=False,
            )
            .distinct()
            .order_by("name")
        )

        # Get health boards with active registered cases
        health_boards = (
            LocalHealthBoard.objects.filter(
                organisation__site__site_is_primary_centre_of_epilepsy_care=True,
                organisation__site__site_is_actively_involved_in_epilepsy_care=True,
                organisation__site__case__isnull=False,
                organisation__site__case__registration__isnull=False,
            )
            .distinct()
            .order_by("name")
        )

        result = [(f"t_{trust.id}", f"Trust: {trust.name}") for trust in trusts]
        result += [(f"h_{hb.id}", f"Health Board: {hb.name}") for hb in health_boards]
        return result

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        value_type, value_id = self.value().split("_", 1)

        if self.value().startswith("t_"):
            # Filter by Trust
            return queryset.filter(
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
                site__case__isnull=False,
                site__case__registration__isnull=False,
                site__organisation__trust__id=value_id,
            )
        elif self.value().startswith("h_"):
            # Filter by Local Health Board
            return queryset.filter(
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
                site__case__isnull=False,
                site__case__registration__isnull=False,
                site__organisation__local_health_board__id=value_id,
            )
        return queryset


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
        "registration__cohort",
        OrganisationFilter,
        TrustOrLocalHealthBoardFilter,
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
        "registration__cohort",
    ]


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
    raw_id_fields = ["epilepsy12_user", "employer_organisation"]
    autocomplete_fields = ["epilepsy12_user", "employer_organisation"]


class OrganisationAdmin(SimpleHistoryAdmin):
    search_fields = ["name", "ods_code"]


class TrustAdmin(SimpleHistoryAdmin):
    search_fields = ["name", "ods_code"]


# register all models
admin.site.register(Epilepsy12User, Epilepsy12UserAdmin)
admin.site.register(AntiEpilepsyMedicine, SimpleHistoryAdmin)
admin.site.register(Assessment, SimpleHistoryAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(Comorbidity, SimpleHistoryAdmin)
admin.site.register(EpilepsyContext, SimpleHistoryAdmin)
admin.site.register(Investigations, SimpleHistoryAdmin)
admin.site.register(OrganisationEmployer, OrganisationEmployerAdmin)


admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(FirstPaediatricAssessment, SimpleHistoryAdmin)
admin.site.register(Management, SimpleHistoryAdmin)
admin.site.register(Registration, SimpleHistoryAdmin)
admin.site.register(Site, SimpleHistoryAdmin)
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
