# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import Syndrome, Syndrome


class SyndromeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Syndrome
        syndrome = serializers.PrimaryKeyRelatedField(queryset=Syndrome.objects.all())
        fields = "__all__"
