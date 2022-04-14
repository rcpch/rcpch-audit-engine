from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(AntiEpilepsyMedicine)
admin.site.register(Assessment)
admin.site.register(Case)
admin.site.register(Comorbidity)
admin.site.register(ElectroClinicalSyndrome)
admin.site.register(EpilepsyContext)
admin.site.register(HospitalTrust)
admin.site.register(InitialAssessment)
admin.site.register(Investigation_Management)
# admin.site.register(Investigations)
admin.site.register(NonEpilepsy)
admin.site.register(Registration)
# admin.site.register(RescueMedicine)
admin.site.register(SeizureCause)
admin.site.register(SeizureType)
