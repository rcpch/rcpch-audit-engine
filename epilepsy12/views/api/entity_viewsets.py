"""
Django Rest Framework Entity Viewsets
"""
# python
# django rest framework
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import permissions, viewsets
from rest_framework import mixins
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import GenericViewSet

# third party
from epilepsy12.serializers.epilepsy_cause_entity_serializer import (
    EpilepsyCauseEntitySerializer,
)
from epilepsy12.serializers.keyword_serializer import KeywordSerializer
from epilepsy12.serializers.organisation_serializer import (
    OrganisationSerializer,
    OrganisationCaseSerializer,
)
from epilepsy12.serializers.antiepilepsymedicine_serializer import (
    AntiEpilepsyMedicineSerializer,
)

from epilepsy12.models import (
    AntiEpilepsyMedicine,
    Organisation,
    Keyword,
    Comorbidity,
)
from epilepsy12.permissions import CanAccessOrganisation


class AntiEpilepsyMedicineViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows antiseizure medicines to be viewed.
    """

    queryset = AntiEpilepsyMedicine.objects.all()
    serializer_class = AntiEpilepsyMedicineSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]


class OrganisationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a list of organisation and community trusts to be viewed.
    """

    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
    lookup_field = "ods_code"

    def retrieve(self, request, ods_code=None):
        """
        API endpoint that retrieves an organisation by ODS Code
        """
        queryset = Organisation.objects.all()
        organisation = get_object_or_404(queryset, ods_code=ods_code)
        self.check_object_permissions(self.request, organisation)
        serializer = OrganisationSerializer(organisation)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        lookup_field="ods_code",
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def cases(self, request, ods_code=None):
        """
        API endpoint that allows a list of all cases associated with a given organisation (retrieved by ODS Code)
        """
        queryset = Organisation.objects.all()
        organisation = get_object_or_404(queryset, ods_code=ods_code)
        serializer = OrganisationCaseSerializer(organisation)
        return Response(serializer.data)


class KeywordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows epilepsy semiology keywords to be viewed.
    """

    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]


class EpilepsyCauseEntityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows all selectable epilepsy causes to be viewed.
    """

    queryset = Comorbidity.objects.all()
    serializer_class = EpilepsyCauseEntitySerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
