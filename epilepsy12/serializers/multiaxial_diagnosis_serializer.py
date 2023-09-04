# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import MultiaxialDiagnosis, Registration, Comorbidity
from epilepsy12.serializers.episode_serializer import EpisodeSerializer
from epilepsy12.serializers.syndrome_serializer import SyndromeSerializer
from epilepsy12.serializers.comorbidity_serializer import ComorbiditySerializer
from epilepsy12.common_view_functions import update_audit_progress, calculate_kpis


class MultiaxialDiagnosisSerializer(serializers.ModelSerializer):
    episodes = EpisodeSerializer(many=True)
    syndromes = SyndromeSerializer(many=True)
    epilepsy_cause = serializers.SlugRelatedField(
        queryset=Comorbidity.objects.all(), slug_field="preferredTerm"
    )
    registration = serializers.PrimaryKeyRelatedField(
        queryset=Registration.objects.all()
    )
    comorbidities = ComorbiditySerializer(many=True)

    class Meta:
        model = MultiaxialDiagnosis
        fields = [
            "syndrome_present",
            "epilepsy_cause_known",
            "epilepsy_cause",
            "epilepsy_cause_categories",
            "relevant_impairments_behavioural_educational",
            "mental_health_screen",
            "mental_health_issue_identified",
            "mental_health_issue",
            "episodes",
            "syndromes",
            "comorbidities",
            "autistic_spectrum_disorder",
            "global_developmental_delay_or_learning_difficulties",
            "global_developmental_delay_or_learning_difficulties_severity",
            "registration",
        ]

    def get_epilepsy_cause(self):
        """
        This is a custom method as the user passes in an SCTID of the epilepsy cause
        This is validated and used to look up the value in the the Comorbidity table
        and passed back to the epilepsy_cause field in the Multiaxial Diagnosis instance in the save()
        """
        sctid = self.context.get("sctid")
        if sctid is not None:
            if Comorbidity.objects.filter(conceptId=sctid).exists():
                self.instance.epilepsy_cause = Comorbidity.objects.filter(
                    conceptId=sctid
                ).first()
            else:
                raise serializers.ValidationError(
                    f"{sctid} is not a valid SNOMED-CT id, or is not in the Epilepsy12 refset."
                )
        else:
            self.instance.epilepsy_cause = None
        return self.instance.epilepsy_cause

    def validate(self, data):
        """
        Validation for all the fields
        """
        if "epilepsy_cause_known" in data:
            if data["epilepsy_cause_known"]:
                if self.context.get("sctid") is None:
                    raise serializers.ValidationError(
                        {
                            "epilepsy_cause error": "A valid epilepsy cause must be supplied if epilepsy_cause_known is set to true. To this, please pass a valid SNOMED-CT conceptId using the `sctid` key."
                        }
                    )
                if "epilepsy_cause_categories" not in data:
                    raise serializers.ValidationError(
                        {
                            "epilepsy_cause_categories": "At least one category must be supplied. Options include [(`Gen`: `Genetic`), (`Imm`, `Immune`), (`Inf`, `Infectious`), (`Met`, `Metabolic`), (`Str`, `Structural`), (`NK`, `Not known`)]."
                        }
                    )
                else:
                    if len(data["epilepsy_cause_categories"]) < 0:
                        raise serializers.ValidationError(
                            {
                                "epilepsy_cause_categories": "At least one category must be supplied. Options include [(`Gen`: `Genetic`), (`Imm`, `Immune`), (`Inf`, `Infectious`), (`Met`, `Metabolic`), (`Str`, `Structural`), (`NK`, `Not known`)]."
                            }
                        )
            else:
                if self.context.get("sctid") is not None:
                    raise serializers.ValidationError(
                        {
                            "epilepsy_cause error": "An epilepsy cause cannot be supplied if epilepsy_cause_known is set to false."
                        }
                    )
                if "epilepsy_cause_categories" in data:
                    if len(data["epilepsy_cause_categories"]) > 0:
                        raise serializers.ValidationError(
                            {
                                "epilepsy_cause_categories": "An epilepsy cause category cannot be supplied if epilepsy_cause_known is set to false."
                            }
                        )
        if "mental_health_issue_identified" in data:
            if data["mental_health_issue_identified"]:
                if "mental_health_issue" not in data:
                    raise serializers.ValidationError(
                        {
                            "mental_health_issue_identified": "Mental health issue must be supplied."
                        }
                    )
                else:
                    if data["mental_health_issue"] is None:
                        raise serializers.ValidationError(
                            {
                                "mental_health_issue_identified": "Mental health issue must be supplied."
                            }
                        )
            else:
                if (
                    "mental_health_issue" in data
                    and data["mental_health_issue"] is not None
                ):
                    raise serializers.ValidationError(
                        {
                            "mental_health_issue": "Mental health issue cannot be supplied if mental_health_issue_identified is set to false."
                        }
                    )
        if (
            "global_developmental_delay_or_learning_difficulties" in data
            and data["global_developmental_delay_or_learning_difficulties"]
        ):
            if "global_developmental_delay_or_learning_difficulties_severity" in data:
                if (
                    data["global_developmental_delay_or_learning_difficulties_severity"]
                    is None
                    or len(
                        data[
                            "global_developmental_delay_or_learning_difficulties_severity"
                        ]
                    )
                    < 1
                ):
                    raise serializers.ValidationError(
                        {
                            "global_developmental_delay_or_learning_difficulties_severity": "A measure of severity of global developmental delay or learning difficulties must be supplied. Options include: (`mild`, `moderate`, `severe`, `profound`, `uncertain`)"
                        }
                    )
            else:
                raise serializers.ValidationError(
                    {
                        "global_developmental_delay_or_learning_difficulties_severity": "A measure of severity of global developmental delay or learning difficulties must be supplied. Options include: (`mild`, `moderate`, `severe`, `profound`, `uncertain`)"
                    }
                )
        else:
            if (
                "global_developmental_delay_or_learning_difficulties_severity" in data
                and len(
                    data["global_developmental_delay_or_learning_difficulties_severity"]
                )
                > 0
            ):
                raise serializers.ValidationError(
                    {
                        "global_developmental_delay_or_learning_difficulties_severity": "A measure of severity of global developmental delay or learning difficulties must ONLY be supplied if global_developmental_delay_or_learning_difficulties is set to true."
                    }
                )

        return data

    def update(self, instance, validated_data):
        """
        Update function called by view on PUT request
        """
        instance.epilepsy_cause_known = validated_data.get(
            "epilepsy_cause_known", instance.epilepsy_cause_known
        )

        instance.epilepsy_cause_categories = validated_data.get(
            "epilepsy_cause_categories", instance.epilepsy_cause_categories
        )
        instance.mental_health_screen = validated_data.get(
            "mental_health_screen", instance.mental_health_screen
        )
        instance.mental_health_issue_identified = validated_data.get(
            "mental_health_issue_identified", instance.mental_health_issue_identified
        )
        instance.mental_health_issue = validated_data.get(
            "mental_health_issue", instance.mental_health_issue
        )
        instance.autistic_spectrum_disorder = validated_data.get(
            "autistic_spectrum_disorder", instance.autistic_spectrum_disorder
        )
        instance.global_developmental_delay_or_learning_difficulties = (
            validated_data.get(
                "global_developmental_delay_or_learning_difficulties",
                instance.global_developmental_delay_or_learning_difficulties,
            )
        )
        instance.global_developmental_delay_or_learning_difficulties_severity = (
            validated_data.get(
                "global_developmental_delay_or_learning_difficulties_severity",
                instance.global_developmental_delay_or_learning_difficulties_severity,
            )
        )

        instance.epilepsy_cause = self.get_epilepsy_cause()

        instance.save()
        update_audit_progress(instance)
        calculate_kpis(instance.registration)
        return instance
