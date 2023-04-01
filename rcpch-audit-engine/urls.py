from rest_framework import routers
from django.contrib import admin
from django.urls import path, include


handler403 = 'epilepsy12.views.rcpch_403'
handler404 = 'epilepsy12.views.rcpch_404'
handler500 = 'epilepsy12.views.rcpch_500'


router = routers.DefaultRouter()

urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('', include('epilepsy12.urls')),
]
