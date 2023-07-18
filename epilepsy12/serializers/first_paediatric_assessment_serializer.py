# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import *
from epilepsy12.common_view_functions import calculate_kpis, update_audit_progress


class FirstPaediatricAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirstPaediatricAssessment
        registration = serializers.PrimaryKeyRelatedField(
            queryset=Registration.objects.all()
        )
        fields = [
            "id",
            "first_paediatric_assessment_in_acute_or_nonacute_setting",
            "has_number_of_episodes_since_the_first_been_documented",
            "general_examination_performed",
            "neurological_examination_performed",
            "developmental_learning_or_schooling_problems",
            "behavioural_or_emotional_problems",
        ]

    def update(self, instance, validated_data):
        instance.first_paediatric_assessment_in_acute_or_nonacute_setting = (
            validated_data.get(
                "first_paediatric_assessment_in_acute_or_nonacute_setting",
                instance.first_paediatric_assessment_in_acute_or_nonacute_setting,
            )
        )
        instance.has_number_of_episodes_since_the_first_been_documented = (
            validated_data.get(
                "has_number_of_episodes_since_the_first_been_documented",
                instance.has_number_of_episodes_since_the_first_been_documented,
            )
        )
        instance.general_examination_performed = validated_data.get(
            "general_examination_performed", instance.general_examination_performed
        )
        instance.neurological_examination_performed = validated_data.get(
            "neurological_examination_performed",
            instance.neurological_examination_performed,
        )
        instance.developmental_learning_or_schooling_problems = validated_data.get(
            "developmental_learning_or_schooling_problems",
            instance.developmental_learning_or_schooling_problems,
        )
        instance.behavioural_or_emotional_problems = validated_data.get(
            "behavioural_or_emotional_problems",
            instance.behavioural_or_emotional_problems,
        )
        instance.save()
        update_audit_progress(instance)
        calculate_kpis(instance.registration)
        return instance
