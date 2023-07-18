"""
Django Rest Framework Site Viewset
"""
# python

# django rest framework
from rest_framework import permissions
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

# third party

# Epilepsy12
from epilepsy12.serializers.site_serializer import SiteSerializer
from epilepsy12.models import Site
from epilepsy12.permissions import CanAccessOrganisation


class SiteViewSet(GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    """
    API endpoint that allows allocated sites to be viewed.
    """

    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
