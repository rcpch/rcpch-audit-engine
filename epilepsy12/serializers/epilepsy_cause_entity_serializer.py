# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import Comorbidity


class EpilepsyCauseEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comorbidity
        fields = "__all__"
