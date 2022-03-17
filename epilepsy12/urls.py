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
    path('eeg', views.eeg, name="eeg"),
    path('patient', views.patient, name="patient"),
]
