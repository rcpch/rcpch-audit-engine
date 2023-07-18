# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import Comorbidity, Syndrome, MultiaxialDiagnosis, SyndromeEntity
from epilepsy12.common_view_functions import update_audit_progress, calculate_kpis


class SyndromeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Syndrome
        multiaxial_diagnosis = serializers.PrimaryKeyRelatedField(
            queryset=MultiaxialDiagnosis.objects.all()
        )
        syndrome = serializers.PrimaryKeyRelatedField(
            queryset=SyndromeEntity.objects.all()
        )
        fields = ["syndrome_diagnosis_date", "syndrome"]

    def update(self, instance, validated_data):
        instance.syndrome_diagnosis_date = validated_data.get(
            "syndrome_diagnosis_date", instance.syndrome_diagnosis_date
        )
        instance.syndrome = validated_data.get("syndrome", instance.syndrome)

        instance.save()
        update_audit_progress(instance)
        calculate_kpis(instance.registration)
        return instance

    def create(self, validated_data):
        instance = Comorbidity.objects.create(**validated_data)
        update_audit_progress(instance)
        calculate_kpis(instance.registration)
        return instance
