"""
Django Rest Framework Assessment Viewsets
"""
# python

# django rest framework
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, permissions

# third party

# Epilepsy12
from epilepsy12.serializers.assessment_serializer import AssessmentSerializer

from epilepsy12.models import Assessment
from epilepsy12.permissions import CanAccessOrganisation


class AssessmentViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows key Epilepsy12 milestones to be viewed.
    """

    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
    lookup_field = "nhs_number"
