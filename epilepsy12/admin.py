from typing import Any
from django.http import HttpResponse
from django.contrib import messages
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.
from .models import *
from .organisational_audit import export_submission_period_as_csv


class Epilepsy12UserAdmin(UserAdmin, SimpleHistoryAdmin):
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
                    # "employer_organisation",
                    # "organisation_employer",
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
                    # "employer_organisation",
                    # "organisation_employer",
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
    search_fields = [
        "first_name",
        "surname",
        "nhs_number",
        "unique_reference_number",
        "date_of_birth",
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
