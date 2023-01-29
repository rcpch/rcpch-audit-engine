from rest_framework import routers
from django.contrib import admin
from django.urls import path, include


handler403 = 'epilepsy12.views.rcpch_403'


router = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('epilepsy12/', include('epilepsy12.urls')),
]
