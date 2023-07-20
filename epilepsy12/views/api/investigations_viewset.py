"""
Django Rest Framework Investigations Viewset
"""
# python

# django rest framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import mixins
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import GenericViewSet

# third party

# Epilepsy12
from epilepsy12.serializers.investigations_serializer import InvestigationsSerializer
from epilepsy12.models import Investigations, Case
from epilepsy12.permissions import CanAccessOrganisation


class InvestigationsViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows a panel of investigations for each registration to be viewed.
    """

    queryset = Investigations.objects.all()
    serializer_class = InvestigationsSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
    lookup_field = "nhs_number"

    def retrieve(self, request, nhs_number=None):
        """
        Retrieve investigations fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "investigations"):
                instance = Investigations.objects.filter(
                    pk=case.registration.investigations.pk
                ).get()
                serializer = InvestigationsSerializer(instance=instance)
                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_200_OK,
        )

    def update(self, request, nhs_number=None):
        """
        Update investigations fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "investigations"):
                instance = Investigations.objects.get(
                    pk=case.registration.investigations.pk
                )
                serializer = InvestigationsSerializer(
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
