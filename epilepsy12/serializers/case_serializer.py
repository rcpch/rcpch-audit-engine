# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import *


class NestedCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ["id", "first_name", "surname", "nhs_number"]


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = [
            "locked",
            "locked_at",
            "locked_by",
            "nhs_number",
            "first_name",
            "surname",
            "sex",
            "date_of_birth",
            "postcode",
            "ethnicity",
            "index_of_multiple_deprivation_quintile",
            "organisations",
        ]
        lookup_field = "nhs_number"
