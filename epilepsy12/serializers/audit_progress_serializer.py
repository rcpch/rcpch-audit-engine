# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import AuditProgress


class AuditProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditProgress
        fields = "__all__"
