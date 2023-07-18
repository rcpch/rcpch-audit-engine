# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import *
from epilepsy12.common_view_functions import calculate_kpis, update_audit_progress


class EpilepsyContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpilepsyContext
        registration = serializers.PrimaryKeyRelatedField(
            queryset=Registration.objects.all()
        )
        fields = [
            "previous_febrile_seizure",
            "previous_acute_symptomatic_seizure",
            "is_there_a_family_history_of_epilepsy",
            "previous_neonatal_seizures",
            "diagnosis_of_epilepsy_withdrawn",
            "were_any_of_the_epileptic_seizures_convulsive",
            "experienced_prolonged_generalized_convulsive_seizures",
            "experienced_prolonged_focal_seizures",
        ]

    def update(self, instance, validated_data):
        instance.previous_febrile_seizure = validated_data.get(
            "previous_febrile_seizure",
            instance.previous_febrile_seizure,
        )
        instance.previous_acute_symptomatic_seizure = validated_data.get(
            "previous_acute_symptomatic_seizure",
            instance.previous_acute_symptomatic_seizure,
        )
        instance.is_there_a_family_history_of_epilepsy = validated_data.get(
            "is_there_a_family_history_of_epilepsy",
            instance.is_there_a_family_history_of_epilepsy,
        )
        instance.previous_neonatal_seizures = validated_data.get(
            "previous_neonatal_seizures",
            instance.previous_neonatal_seizures,
        )
        instance.diagnosis_of_epilepsy_withdrawn = validated_data.get(
            "diagnosis_of_epilepsy_withdrawn",
            instance.diagnosis_of_epilepsy_withdrawn,
        )
        instance.were_any_of_the_epileptic_seizures_convulsive = validated_data.get(
            "were_any_of_the_epileptic_seizures_convulsive",
            instance.were_any_of_the_epileptic_seizures_convulsive,
        )
        instance.experienced_prolonged_generalized_convulsive_seizures = (
            validated_data.get(
                "experienced_prolonged_generalized_convulsive_seizures",
                instance.experienced_prolonged_generalized_convulsive_seizures,
            )
        )
        instance.experienced_prolonged_focal_seizures = validated_data.get(
            "experienced_prolonged_focal_seizures",
            instance.experienced_prolonged_focal_seizures,
        )
        instance.save()
        update_audit_progress(instance)
        calculate_kpis(instance.registration)
        return instance
