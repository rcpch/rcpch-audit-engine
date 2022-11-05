from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from ..epilepsy12.views import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

handler403 = 'epilepsy12.views.rcpch_403'

urlpatterns = [
    path('', include('epilepsy12.urls')),
    path('admin/', admin.site.urls),
    path('epilepsy12/', include('epilepsy12.urls')),
    path('epilepsy12/', include('django.contrib.auth.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    # rest framework paths
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
