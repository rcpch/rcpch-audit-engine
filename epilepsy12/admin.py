from atexit import unregister
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import *

from .forms import Epilepsy12UserChangeForm, Epilepsy12UserCreationForm


class Epilepsy12UserAdmin(UserAdmin):
    add_form = Epilepsy12UserCreationForm
    form = Epilepsy12UserChangeForm
    order = ('surname')
    model = Epilepsy12User
    search_fields = ('email', 'username', 'surname',
                     'role', 'hospital_employer', 'is_active',)
    list_display = ("username", "email", "title", "first_name", "surname",
                    "is_active", "twitter_handle", "role", "hospital_employer", "is_rcpch_audit_team_member")
    list_filter = ("is_active", "role", "hospital_employer",)
    fieldsets = (
        (
            None, {
                'fields': (
                    'username',
                    'title',
                    'first_name',
                    'surname',
                )
            }
        ),
        (
            'Epilepsy12 Centre', {
                'fields': (
                    'hospital_employer',
                    'role'
                )
            }
        ),
        (
            'Contacts', {
                'fields': (
                    'email',
                    'twitter_handle'
                )
            }
        ),
        (
            'Permissions', {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_rcpch_audit_team_member',
                    'is_superuser',
                )
            }
        ),
        (
            'Group Permissions', {
                'classes': ('collapse',),
                'fields': (
                    'groups', 'user_permissions',
                )
            }
        ),
        (
            'Personal', {
                'fields': ('bio',)
            }
        ),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'title', 'first_name', 'surname', 'password1', 'password2', 'is_staff', 'is_active', 'is_rcpch_audit_team_member', 'role', 'hospital_employer')
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields['is_superuser'].disabled = True
            form.base_fields['is_rcpch_audit_team_member'].disabled = True
            form.base_fields['groups'].disabled = True
        if request.user.groups.filter(name='trust_audit_team_edit_access'):
            form.base_fields['groups'].disabled = True
            form.base_fields['username'].disabled = True
            form.base_fields['first_name'].disabled = True
            form.base_fields['surname'].disabled = True
            form.base_fields['title'].disabled = True
            form.base_fields['email'].disabled = True
            form.base_fields['is_staff'].disabled = True
        return form


admin.site.register(Epilepsy12User, Epilepsy12UserAdmin)
admin.site.register(AntiEpilepsyMedicine)
admin.site.register(Assessment)
admin.site.register(Case)
admin.site.register(Comorbidity)
admin.site.register(EpilepsyContext)
admin.site.register(Investigations)
admin.site.register(HospitalTrust)
admin.site.register(InitialAssessment)
admin.site.register(Management)
admin.site.register(Registration)
admin.site.register(Keyword)
admin.site.register(Site)
admin.site.register(AuditProgress)
admin.site.register(Episode)
admin.site.register(MultiaxialDiagnosis)
admin.site.register(Syndrome)

admin.site.site_header = 'Epilepsy12 admin'
admin.site.site_title = 'Epilepsy12 admin'
