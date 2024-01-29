from rest_framework import routers
from django.contrib import admin
from django.urls import path, include
from django.contrib.admindocs import urls
from two_factor.urls import urlpatterns as tf_urls
from epilepsy12.views import RCPCHLoginView

handler403 = "epilepsy12.views.rcpch_403"
handler404 = "epilepsy12.views.rcpch_404"
handler500 = "epilepsy12.views.rcpch_500"


router = routers.DefaultRouter()

# OVERRIDE TWO_FACTOR LOGIN URL TO CAPTCHA LOGIN
for item in tf_urls:
    if type(item) == list:
        for url_pattern in item:
            if vars(url_pattern).get('name') == 'login':
                url_pattern.callback = RCPCHLoginView.as_view()
        break

urlpatterns = [
    path("admin/doc/", include(urls)),
    path("admin/", admin.site.urls),
    path('', include(tf_urls)),
    path("", include("epilepsy12.urls")),
]
