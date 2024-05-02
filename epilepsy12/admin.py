from typing import Any
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.
from .models import *


class Epilepsy12UserAdmin(UserAdmin, SimpleHistoryAdmin):
    ordering = ["email"]
    model = Epilepsy12User
    search_fields = (
        "email",
        "surname",
        "role",
        "is_active",
    )
    list_filter = (
        "is_active",
        "role",
        "organisation_employer",
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
        ("Epilepsy12 Centre", {"fields": ("organisation_employer", "role")}),
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
                    "organisation_employer",
                    "is_superuser",
                    "groups",
                ),
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["organisation_employer"].required = False
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
    search_fields = ["first_name", "surname", "nhs_number", "date_of_birth"]


admin.site.register(Epilepsy12User, Epilepsy12UserAdmin)
admin.site.register(AntiEpilepsyMedicine, SimpleHistoryAdmin)
admin.site.register(Assessment, SimpleHistoryAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(Comorbidity, SimpleHistoryAdmin)
admin.site.register(EpilepsyContext, SimpleHistoryAdmin)
admin.site.register(Investigations, SimpleHistoryAdmin)
admin.site.register(Organisation, SimpleHistoryAdmin)
admin.site.register(FirstPaediatricAssessment, SimpleHistoryAdmin)
admin.site.register(Management, SimpleHistoryAdmin)
admin.site.register(Registration, SimpleHistoryAdmin)
admin.site.register(Site, SimpleHistoryAdmin)
admin.site.register(AuditProgress)
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
admin.site.register(Trust)
admin.site.register(LocalHealthBoard)
admin.site.register(OPENUKNetwork)


admin.site.site_header = "Epilepsy12 admin"
admin.site.site_title = "Epilepsy12 admin"
admin.site.index_title = "Epilepsy12"
admin.site.site_url = "/"
