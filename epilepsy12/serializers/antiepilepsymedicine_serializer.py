# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import Management, AntiEpilepsyMedicine
from epilepsy12.common_view_functions import update_audit_progress, calculate_kpis


class AntiEpilepsyMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntiEpilepsyMedicine
        management = serializers.PrimaryKeyRelatedField(
            queryset=Management.objects.all()
        )
        fields = [
            "medicine_name",
            "is_rescue_medicine",
            "antiepilepsy_medicine_snomed_code",
            "antiepilepsy_medicine_snomed_preferred_name",
            "antiepilepsy_medicine_start_date",
            "antiepilepsy_medicine_stop_date",
            "antiepilepsy_medicine_risk_discussed",
            "is_a_pregnancy_prevention_programme_needed",
            "is_a_pregnancy_prevention_programme_in_place",
        ]

        def update(self, instance, validated_data):
            instance.medicine_name = validated_data.get(
                "medicine_name", instance.medicine_name
            )
            instance.is_rescue_medicine = validated_data.get(
                "is_rescue_medicine", instance.is_rescue_medicine
            )
            instance.antiepilepsy_medicine_snomed_code = validated_data.get(
                "antiepilepsy_medicine_snomed_code",
                instance.antiepilepsy_medicine_snomed_code,
            )
            instance.antiepilepsy_medicine_snomed_preferred_name = validated_data.get(
                "antiepilepsy_medicine_snomed_preferred_name",
                instance.antiepilepsy_medicine_snomed_preferred_name,
            )
            instance.antiepilepsy_medicine_start_date = validated_data.get(
                "antiepilepsy_medicine_start_date",
                instance.antiepilepsy_medicine_start_date,
            )
            instance.antiepilepsy_medicine_stop_date = validated_data.get(
                "antiepilepsy_medicine_stop_date",
                instance.antiepilepsy_medicine_stop_date,
            )
            instance.antiepilepsy_medicine_risk_discussed = validated_data.get(
                "antiepilepsy_medicine_risk_discussed",
                instance.antiepilepsy_medicine_risk_discussed,
            )
            instance.is_a_pregnancy_prevention_programme_needed = validated_data.get(
                "is_a_pregnancy_prevention_programme_needed",
                instance.is_a_pregnancy_prevention_programme_needed,
            )
            instance.is_a_pregnancy_prevention_programme_in_place = validated_data.get(
                "is_a_pregnancy_prevention_programme_in_place",
                instance.is_a_pregnancy_prevention_programme_in_place,
            )

            instance.save()
            update_audit_progress(instance)
            calculate_kpis(instance.registration)
            return instance
