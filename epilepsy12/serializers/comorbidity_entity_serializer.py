# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import ComorbidityEntity


class ComorbidityEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComorbidityEntity
        fields = "__all__"
