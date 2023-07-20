# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import EpilepsyCauseEntity


class EpilepsyCauseEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = EpilepsyCauseEntity
        fields = "__all__"
