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
                     'role', 'hospital_trust', 'is_active',)
    list_display = ("username", "email", "title", "first_name", "surname",
                    "is_active", "twitter_handle", "role", "hospital_trust",)
    list_filter = ("is_active", "role", "hospital_trust",)
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
                    'hospital_trust',
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
            'fields': ('email', 'username', 'title', 'first_name', 'surname', 'password1', 'password2', 'is_staff', 'is_active', 'role', 'hospital_trust')
        }),
    )


admin.site.register(Epilepsy12User, Epilepsy12UserAdmin)
admin.site.register(AntiEpilepsyMedicine)
admin.site.register(Assessment)
admin.site.register(Case)
admin.site.register(Comorbidity)
admin.site.register(ElectroClinicalSyndrome)
admin.site.register(EpilepsyContext)
admin.site.register(HospitalTrust)
admin.site.register(InitialAssessment)
admin.site.register(Investigation_Management)
admin.site.register(NonEpilepsy)
admin.site.register(Registration)
admin.site.register(SeizureCause)
admin.site.register(SeizureType)
admin.site.register(Keyword)
admin.site.register(DESSCRIBE)
