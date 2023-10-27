"""
Django Rest Framework Epilepsy12User Viewset
"""
# python

# django rest framework
from rest_framework import permissions, viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

# third party
from django_filters.rest_framework import DjangoFilterBackend
from epilepsy12.serializers.epilepsy12user_serializer import Epilepsy12UserSerializer

from epilepsy12.models import Epilepsy12User
from epilepsy12.permissions import CanAccessOrganisation


class Epilepsy12UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """

    queryset = Epilepsy12User.objects.all().order_by("-surname")
    serializer_class = Epilepsy12UserSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
