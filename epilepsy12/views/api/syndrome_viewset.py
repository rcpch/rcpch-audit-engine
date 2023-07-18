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


class SyndromeViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows each syndrome to be viewed.
    """

    queryset = Syndrome.objects.all()
    serializer_class = SyndromeSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
    lookup_field = "nhs_number"

    def retrieve(self, request, nhs_number=None):
        """
        Retrieve multiaxial diagnosis fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "multiaxialdiagnosis"):
                if hasattr(case.registration.multiaxialdiagnosis, "syndrome"):
                    instance = Syndrome.objects.filter(
                        multiaxialdiagnosis=case.registration.multiaxialdiagnosis
                    )
                    serializer = SyndromeSerializer(instance=instance)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {f"{case} has no valid syndromes documented yet."},
                        status=status.HTTP_200_OK,
                    )
        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_200_OK,
        )

    def update(self, request, nhs_number=None):
        """
        Update multiaxial diagnosis fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "multiaxialdiagnosis"):
                if hasattr(case.registration.multiaxialdiagnosis, "syndrome"):
                    instance = Syndrome.objects.get(
                        multiaxial_diagnosis=case.registration.multiaxialdiagnosis.pk
                    )
                    serializer = Syndrome(instance=instance, data=request.data)
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

    def create(self, request, nhs_number=None):
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "multiaxialdiagnosis"):
                serializer = Syndrome(data=request.data)
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


class SyndromeEntityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows all selectable syndromes to be viewed.
    """

    queryset = SyndromeEntity.objects.all()
    serializer_class = SyndromeEntitySerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
