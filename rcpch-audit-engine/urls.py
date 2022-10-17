from django.contrib import admin
from django.urls import path, include

handler403 = 'epilepsy12.views.rcpch_403'

urlpatterns = [
    path('', include('epilepsy12.urls')),
    path('admin/', admin.site.urls),
    path('epilepsy12/', include('epilepsy12.urls')),
    path('epilepsy12/', include('django.contrib.auth.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
