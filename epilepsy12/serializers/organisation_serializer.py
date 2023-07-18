# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import Organisation
from epilepsy12.serializers.case_serializer import CaseSerializer


class OrganisationCaseSerializer(serializers.ModelSerializer):
    cases = CaseSerializer(many=True, read_only=True)

    class Meta:
        model = Organisation
        fields = [
            "ODSCode",
            "OrganisationName",
            "Website",
            "Address1",
            "Address2",
            "Address3",
            "City",
            "County",
            "Latitude",
            "Longitude",
            "Postcode",
            "Geocode_Coordinates",
            "ParentOrganisation_ODSCode",
            "ParentOrganisation_OrganisationName",
            "LastUpdatedDate",
            "cases",
        ]


class OrganisationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organisation
        fields = [
            "ODSCode",
            "OrganisationName",
            "Website",
            "Address1",
            "Address2",
            "Address3",
            "City",
            "County",
            "Latitude",
            "Longitude",
            "Postcode",
            "Geocode_Coordinates",
            "ParentOrganisation_ODSCode",
            "ParentOrganisation_OrganisationName",
            "LastUpdatedDate",
        ]
