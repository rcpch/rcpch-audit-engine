from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('database', views.database, name="database"),
    path('cases', views.hospital, name="cases"),
    path('case/<int:id>/update', views.update_case, name="update_case"),
    path('case/create', views.create_case, name="create_case"),
    path('case/<int:id>/delete', views.delete_case, name="delete_case"),
    path('case/<int:id>/register',
         views.register, name='register'),
    path('registration/<int:id>/update',
         views.update_registration, name="update_registration"),
    path('assessment/<int:case_id>/create',
         views.create_initial_assessment, name="create_initial_assessment"),
    path('assessment/<int:case_id>/update',
         views.update_initial_assessment, name="update_initial_assessment"),
    path('multiaxial_description/<int:id>/create',
         views.create_multiaxial_description, name='create_multiaxial_description'),
    path('multiaxial_description/<int:id>/update',
         views.update_multiaxial_description, name='update_multiaxial_description'),
    path('epilepsy_context/<int:id>/create',
         views.create_epilepsy_context, name='create_epilepsy_context'),
    path('epilepsy_context/<int:id>/update',
         views.update_epilepsy_context, name='update_epilepsy_context'),
    path('investigation_management/<int:id>/create',
         views.create_investigation_management, name='create_investigation_management'),
    path('investigation_management/<int:id>/update',
         views.update_investigation_management, name='update_investigation_management'),
    path('eeg', views.eeg, name="eeg"),
    path('patient', views.patient, name="patient")
]
