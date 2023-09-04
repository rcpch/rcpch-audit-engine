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
            "ods_code",
            "name",
            "website",
            "address1",
            "address2",
            "address3",
            "city",
            "county",
            "latitude",
            "longitude",
            "postcode",
            "geocode_coordinates",
            "trust__ods_code",
            "trust__trust_name",
            "LastUpdatedDate",
            "cases",
        ]


class OrganisationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organisation
        fields = [
            "ods_code",
            "name",
            "website",
            "address1",
            "address2",
            "address3",
            "city",
            "county",
            "latitude",
            "longitude",
            "postcode",
            "geocode_coordinates",
            "trust__ods_code",
            "trust__trust_name",
            "LastUpdatedDate",
        ]
