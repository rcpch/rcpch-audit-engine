"""
Django Rest Framework Episode Viewset
"""
# python

# django
from django.shortcuts import get_object_or_404

# django rest framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

# third party

# epilepsy12
from epilepsy12.serializers.episode_serializer import EpisodeSerializer
from epilepsy12.serializers.multiaxial_diagnosis_serializer import (
    MultiaxialDiagnosisSerializer,
)
from epilepsy12.models import (
    Case,
    Episode,
    MultiaxialDiagnosis,
)
from epilepsy12.permissions import CanAccessOrganisation


class EpisodeViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows each seizure episode to be viewed.
    """

    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
    lookup_field = "nhs_number"

    def retrieve(self, request, pk=None):
        """
        Retrieve multiaxial diagnosis fields by NHS number
        """
        instance = Episode.objects.get(pk=pk)
        serializer = EpisodeSerializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, nhs_number=None):
        """
        Update multiaxial diagnosis fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "multiaxialdiagnosis"):
                instance = MultiaxialDiagnosis.objects.get(
                    pk=case.registration.multiaxialdiagnosis.pk
                )
                serializer = MultiaxialDiagnosisSerializer(
                    instance=instance, data=request.data
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_400_BAD_REQUEST,
        )
