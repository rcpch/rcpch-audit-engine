from . import views
from .view_folder import HospitalAutocomplete
from .view_folder import SemiologyKeywordAutocomplete
from .views import SignUpView
from django.urls import path

urlpatterns = [
    path('', views.index, name="index"),
    path('database', views.database, name="database"),
    path('hospital', views.hospital_reports, name="hospital_reports"),
    path('cases', views.case_list, name="cases"),
    path('case/<int:id>/update', views.update_case, name="update_case"),
    path('case/create', views.create_case, name="create_case"),
    path('case/<int:id>/delete', views.delete_case, name="delete_case"),
    path('case/<int:id>/register',
         views.register, name='register'),
    path('registration/<int:id>/update',
         views.update_registration, name="update_registration"),
    path('initial_assessment/<int:case_id>/create',
         views.create_initial_assessment, name="create_initial_assessment"),
    path('initial_assessment/<int:case_id>/update',
         views.update_initial_assessment, name="update_initial_assessment"),
    path('assessment/<int:case_id>/create',
         views.create_assessment, name="create_assessment"),
    path('assessment/<int:case_id>/update',
         views.update_assessment, name="update_assessment"),
    path('multiaxial_description/<int:case_id>',
         views.multiaxial_description, name='multiaxial_description'),
    path('epilepsy_context/<int:case_id>/create',
         views.create_epilepsy_context, name='create_epilepsy_context'),
    path('epilepsy_context/<int:case_id>/update',
         views.update_epilepsy_context, name='update_epilepsy_context'),
    path('comorbidity/<int:case_id>/create',
         views.create_comorbidity, name="create_comorbidity"),
    path('comorbidity/<int:case_id>/update',
         views.update_comorbidity, name="update_comorbidity"),
    path('investigation_management/<int:case_id>/create',
         views.create_investigation_management, name='create_investigation_management'),
    path('investigation_management/<int:case_id>/update',
         views.update_investigation_management, name='update_investigation_management'),
    path('eeg', views.eeg, name="eeg"),
    path('patient', views.patient, name="patient"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path('hospital-autocomplete/', HospitalAutocomplete.as_view(),
         name='hospital-autocomplete'),
    path('semiology-keyword-autocomplete/', SemiologyKeywordAutocomplete.as_view(),
         name='semiology-keyword-autocomplete'),
]

htmx_paths = [
    path('htmx/<int:desscribe_id>/description',
         views.edit_description, name='edit_description'),
    path('htmx/<int:desscribe_id>/description_keyword/<int:description_keyword_id>/delete',
         views.delete_description_keyword, name='delete_description_keyword'),
    path('htmx/<int:desscribe_id>/epilepsy_or_nonepilepsy_status_changed',
         views.epilepsy_or_nonepilepsy_status_changed, name='epilepsy_or_nonepilepsy_status_changed'),
    path('htmx/<int:desscribe_id>/epilepsy_onset_changed',
         views.epilepsy_onset_changed, name='epilepsy_onset_changed'),
    path('htmx/<int:desscribe_id>/focal_onset_epilepsy_checked_changed',
         views.focal_onset_epilepsy_checked_changed, name='focal_onset_epilepsy_checked_changed'),
    path('htmx/seizure_cause_main',
         views.seizure_cause_main, name='seizure_cause_main')
]

urlpatterns += htmx_paths
