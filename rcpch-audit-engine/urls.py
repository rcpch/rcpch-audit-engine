from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('', include('epilepsy12.urls')),
    path('admin/', admin.site.urls),
    path('epilepsy12/', include('epilepsy12.urls')),
    path('epilepsy12/', include('django.contrib.auth.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    # reactive 3rd party library
    path('unicorn/', include('django_unicorn.urls')),
]
