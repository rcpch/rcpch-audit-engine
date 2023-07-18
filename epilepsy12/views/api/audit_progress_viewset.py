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
from epilepsy12.serializers.audit_progress_serializer import AuditProgressSerializer
from epilepsy12.models import AuditProgress
from epilepsy12.permissions import CanAccessOrganisation


class AuditProgressViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows a child's progress through audit completion to be viewed.
    """

    queryset = AuditProgress.objects.all()
    serializer_class = AuditProgressSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
