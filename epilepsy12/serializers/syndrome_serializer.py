# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import Case, Syndrome, MultiaxialDiagnosis, SyndromeEntity
from epilepsy12.common_view_functions import update_audit_progress, calculate_kpis


class SyndromeSerializer(serializers.ModelSerializer):
    syndrome = serializers.SlugRelatedField(read_only=True, slug_field="syndrome_name")

    class Meta:
        model = Syndrome
        multiaxial_diagnosis = serializers.PrimaryKeyRelatedField(
            queryset=MultiaxialDiagnosis.objects.all()
        )
        fields = ["syndrome_diagnosis_date", "syndrome", "id"]

    def update(self, instance, validated_data):
        instance.syndrome_diagnosis_date = validated_data.get(
            "syndrome_diagnosis_date", instance.syndrome_diagnosis_date
        )
        syndrome_name = self.context.get("syndrome_name")
        syndrome = SyndromeEntity.objects.get(syndrome_name=syndrome_name)
        instance.syndrome = syndrome
        instance.save()

        update_audit_progress(instance.multiaxial_diagnosis.registration)
        calculate_kpis(instance.multiaxial_diagnosis.registration)
        return instance

    def create(self, validated_data):
        nhs_number = self.context.get("nhs_number")
        try:
            case = Case.objects.get(nhs_number=nhs_number)
        except Exception as error:
            raise serializers.ValidationError({"create syndrome": error})
        syndrome_name = self.context.get("syndrome_name")
        syndrome = SyndromeEntity.objects.get(syndrome_name=syndrome_name)
        instance = Syndrome.objects.create(
            multiaxial_diagnosis=case.registration.multiaxialdiagnosis,
            syndrome=syndrome,
            syndrome_diagnosis_date=validated_data.get("syndrome_diagnosis_date"),
        )
        # set multiaxial diagnosis syndrome present to true
        multiaxialdiagnosis = case.registration.multiaxialdiagnosis
        multiaxialdiagnosis.syndrome_present = True
        multiaxialdiagnosis.save()

        update_audit_progress(case.registration)
        calculate_kpis(case.registration)
        return instance
