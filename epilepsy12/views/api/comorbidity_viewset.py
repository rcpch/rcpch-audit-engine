"""
Django Rest Framework Comorbidity Viewsets
"""
# python

# django rest framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions, viewsets
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

# third party
from epilepsy12.serializers.comorbidity_serializer import ComorbiditySerializer
from epilepsy12.serializers.comorbidity_entity_serializer import (
    ComorbidityEntitySerializer,
)

from epilepsy12.models import Comorbidity, Comorbidity
from epilepsy12.permissions import CanAccessOrganisation


class ComorbidityViewSet(GenericViewSet, mixins.UpdateModelMixin):
    """
    API endpoint that allows each comorbidity to be updated by id.
    Creation or list of comorbidities occurs through the case viewset.
    """

    queryset = Comorbidity.objects.all()
    serializer_class = ComorbiditySerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, pk=None):
        """
        Update comorbidity fields by id
        """

        if Comorbidity.objects.filter(pk=pk).exists():
            instance = Comorbidity.objects.get(pk=pk)
            context = {
                "comorbidityentity_sctid": self.request.data.get(
                    "comorbidityentity_sctid", None
                )
            }
            serializer = ComorbiditySerializer(
                instance=instance, data=request.data, context=context
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {
                    "comorbidity update": "No comorbidity found. Did you supply the correct id?"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ComorbidityEntityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows all selectable syndromes to be viewed.
    """

    queryset = Comorbidity.objects.all()
    serializer_class = ComorbidityEntitySerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
