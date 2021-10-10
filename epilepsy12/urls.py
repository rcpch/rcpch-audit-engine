from django.urls import path, include
from django.contrib import admin

urlpatterns = {
    path('backend/', include('backend.urls')),
    path('admin/', admin.site.urls),
}