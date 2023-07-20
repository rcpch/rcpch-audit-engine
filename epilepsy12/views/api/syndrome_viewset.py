"""
Django Rest Framework Syndrome Viewset
"""
# python
# django rest framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework import permissions, viewsets

# third party
from django_filters.rest_framework import DjangoFilterBackend
from epilepsy12.serializers.syndrome_serializer import SyndromeSerializer
from epilepsy12.serializers.syndrome_entity_serializer import SyndromeEntitySerializer

from epilepsy12.models import Case, Syndrome, SyndromeEntity
from epilepsy12.permissions import CanAccessOrganisation


class SyndromeViewSet(GenericViewSet, mixins.UpdateModelMixin):
    """
    API endpoint that allows each syndrome to be updated by id.
    Creation or list of comorbidities occurs through the case viewset.
    """

    queryset = Syndrome.objects.all()
    serializer_class = SyndromeSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]

    def update(self, request, pk=None):
        """
        Update multiaxial diagnosis fields by NHS number
        """
        instance = Syndrome.objects.get(pk=pk)
        context = {"syndrome_name": request.data.get("syndrome_name", None)}
        serializer = SyndromeSerializer(
            instance=instance, data=request.data, context=context
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SyndromeEntityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows all selectable syndromes to be viewed.
    """

    queryset = SyndromeEntity.objects.all()
    serializer_class = SyndromeEntitySerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
