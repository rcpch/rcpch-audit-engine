from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('database', views.database, name="database"),
    path('hospital', views.hospital, name="hospital"),
    path('eeg', views.eeg, name="eeg"),
    path('patient', views.patient, name="patient")
]