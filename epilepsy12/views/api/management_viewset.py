"""
Django Rest Framework Management Viewset
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
from epilepsy12.serializers.management_serializer import ManagementSerializer
from epilepsy12.models import Management, Case
from epilepsy12.permissions import CanAccessOrganisation


class ManagementViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows management plans (including medications and individualised care plans) to be viewed.
    """

    queryset = Management.objects.all()
    serializer_class = ManagementSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
    lookup_field = "nhs_number"

    def retrieve(self, request, nhs_number=None):
        """
        Retrieve management fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "management"):
                instance = Management.objects.filter(
                    pk=case.registration.management.pk
                ).get()
                serializer = ManagementSerializer(instance=instance)
                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_200_OK,
        )

    def update(self, request, nhs_number=None):
        """
        Update management fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "management"):
                instance = Management.objects.get(pk=case.registration.management.pk)
                serializer = ManagementSerializer(instance=instance, data=request.data)
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
