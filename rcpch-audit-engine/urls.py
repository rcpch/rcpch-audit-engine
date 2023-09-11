from rest_framework import routers
from django.contrib import admin
from django.urls import path, include
from django.contrib.admindocs import urls
from two_factor.urls import urlpatterns as tf_urls


handler403 = "epilepsy12.views.rcpch_403"
handler404 = "epilepsy12.views.rcpch_404"
handler500 = "epilepsy12.views.rcpch_500"


router = routers.DefaultRouter()

urlpatterns = [
    path("admin/doc/", include(urls)),
    path("admin/", admin.site.urls),
    path("", include("epilepsy12.urls")),
    path('', include(tf_urls)),
]
