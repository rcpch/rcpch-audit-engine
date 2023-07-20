# Python imports
from datetime import datetime

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import *


def is_future_date(value):
    if value > datetime.now().date():
        raise serializers.ValidationError(
            {
                "registration_date": "First paediatric assessment cannot be in the future."
            }
        )
    return value


def is_true(value):
    if not value:
        raise serializers.ValidationError(
            {
                "eligibility_criteria_met": "Eligibility criteria must have been met to be registered in Epilepsy12."
            }
        )
    return value


class RegistrationSerializer(serializers.ModelSerializer):
    registration_close_date = serializers.DateField(read_only=True)
    cohort = serializers.IntegerField(read_only=True)
    registration_date = serializers.DateField(validators=[is_future_date])
    eligibility_criteria_met = serializers.BooleanField(
        required=True, validators=[is_true]
    )

    class Meta:
        model = Registration
        case = serializers.PrimaryKeyRelatedField(queryset=Case.objects.all())
        audit_progress = serializers.PrimaryKeyRelatedField(
            queryset=AuditProgress.objects.all()
        )
        fields = [
            "pk",
            "case",
            "registration_date",
            "registration_close_date",
            "cohort",
            "eligibility_criteria_met",
            "case",
        ]

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
