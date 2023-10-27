# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import MultiaxialDiagnosis, Episode, Case
from epilepsy12.common_view_functions import calculate_kpis, update_audit_progress


class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        multiaxial_diagnosis = serializers.PrimaryKeyRelatedField(
            queryset=MultiaxialDiagnosis.objects.all()
        )
        fields = [
            "seizure_onset_date",
            "seizure_onset_date_confidence",
            "episode_definition",
            "has_description_of_the_episode_or_episodes_been_gathered",
            "description",
            "description_keywords",
            "epilepsy_or_nonepilepsy_status",
            "epileptic_seizure_onset_type",
            "nonepileptic_seizure_type",
            "epileptic_generalised_onset",
            "focal_onset_impaired_awareness",
            "focal_onset_automatisms",
            "focal_onset_atonic",
            "focal_onset_clonic",
            "focal_onset_left",
            "focal_onset_right",
            "focal_onset_epileptic_spasms",
            "focal_onset_hyperkinetic",
            "focal_onset_myoclonic",
            "focal_onset_tonic",
            "focal_onset_autonomic",
            "focal_onset_behavioural_arrest",
            "focal_onset_cognitive",
            "focal_onset_emotional",
            "focal_onset_sensory",
            "focal_onset_centrotemporal",
            "focal_onset_temporal",
            "focal_onset_frontal",
            "focal_onset_parietal",
            "focal_onset_occipital",
            "focal_onset_gelastic",
            "focal_onset_focal_to_bilateral_tonic_clonic",
            "nonepileptic_seizure_unknown_onset",
            "nonepileptic_seizure_syncope",
            "nonepileptic_seizure_behavioural",
            "nonepileptic_seizure_sleep",
            "nonepileptic_seizure_paroxysmal",
            "nonepileptic_seizure_migraine",
            "nonepileptic_seizure_miscellaneous",
            "nonepileptic_seizure_other",
        ]

        def update(self, instance, validated_data):
            instance.seizure_onset_date = validated_data.get(
                "seizure_onset_date", instance.seizure_onset_date
            )
            instance.seizure_onset_date_confidence = validated_data.get(
                "seizure_onset_date_confidence", instance.seizure_onset_date_confidence
            )
            instance.episode_definition = validated_data.get(
                "episode_definition", instance.episode_definition
            )
            instance.has_description_of_the_episode_or_episodes_been_gathered = (
                validated_data.get(
                    "has_description_of_the_episode_or_episodes_been_gathered",
                    instance.has_description_of_the_episode_or_episodes_been_gathered,
                )
            )
            instance.description = validated_data.get(
                "description", instance.description
            )
            instance.description_keywords = validated_data.get(
                "description_keywords", instance.description_keywords
            )
            instance.epilepsy_or_nonepilepsy_status = validated_data.get(
                "epilepsy_or_nonepilepsy_status",
                instance.epilepsy_or_nonepilepsy_status,
            )
            instance.epileptic_seizure_onset_type = validated_data.get(
                "epileptic_seizure_onset_type", instance.epileptic_seizure_onset_type
            )
            instance.nonepileptic_seizure_type = validated_data.get(
                "nonepileptic_seizure_type", instance.nonepileptic_seizure_type
            )
            instance.epileptic_generalised_onset = validated_data.get(
                "epileptic_generalised_onset", instance.epileptic_generalised_onset
            )
            instance.focal_onset_impaired_awareness = validated_data.get(
                "focal_onset_impaired_awareness",
                instance.focal_onset_impaired_awareness,
            )
            instance.focal_onset_automatisms = validated_data.get(
                "focal_onset_automatisms", instance.focal_onset_automatisms
            )
            instance.focal_onset_atonic = validated_data.get(
                "focal_onset_atonic", instance.focal_onset_atonic
            )
            instance.focal_onset_clonic = validated_data.get(
                "focal_onset_clonic", instance.focal_onset_clonic
            )
            instance.focal_onset_left = validated_data.get(
                "focal_onset_left", instance.focal_onset_left
            )
            instance.focal_onset_right = validated_data.get(
                "focal_onset_right", instance.focal_onset_right
            )
            instance.focal_onset_epileptic_spasms = validated_data.get(
                "focal_onset_epileptic_spasms", instance.focal_onset_epileptic_spasms
            )
            instance.focal_onset_hyperkinetic = validated_data.get(
                "focal_onset_hyperkinetic", instance.focal_onset_hyperkinetic
            )
            instance.focal_onset_myoclonic = validated_data.get(
                "focal_onset_myoclonic", instance.focal_onset_myoclonic
            )
            instance.focal_onset_tonic = validated_data.get(
                "focal_onset_tonic", instance.focal_onset_tonic
            )
            instance.focal_onset_autonomic = validated_data.get(
                "focal_onset_autonomic", instance.focal_onset_autonomic
            )
            instance.focal_onset_behavioural_arrest = validated_data.get(
                "focal_onset_behavioural_arrest",
                instance.focal_onset_behavioural_arrest,
            )
            instance.focal_onset_cognitive = validated_data.get(
                "focal_onset_cognitive", instance.focal_onset_cognitive
            )
            instance.focal_onset_emotional = validated_data.get(
                "focal_onset_emotional", instance.focal_onset_emotional
            )
            instance.focal_onset_sensory = validated_data.get(
                "focal_onset_sensory", instance.focal_onset_sensory
            )
            instance.focal_onset_centrotemporal = validated_data.get(
                "focal_onset_centrotemporal", instance.focal_onset_centrotemporal
            )
            instance.focal_onset_temporal = validated_data.get(
                "focal_onset_temporal", instance.focal_onset_temporal
            )
            instance.focal_onset_frontal = validated_data.get(
                "focal_onset_frontal", instance.focal_onset_frontal
            )
            instance.focal_onset_parietal = validated_data.get(
                "focal_onset_parietal", instance.focal_onset_parietal
            )
            instance.focal_onset_occipital = validated_data.get(
                "focal_onset_occipital", instance.focal_onset_occipital
            )
            instance.focal_onset_gelastic = validated_data.get(
                "focal_onset_gelastic", instance.focal_onset_gelastic
            )
            instance.focal_onset_focal_to_bilateral_tonic_clonic = validated_data.get(
                "focal_onset_focal_to_bilateral_tonic_clonic",
                instance.focal_onset_focal_to_bilateral_tonic_clonic,
            )
            instance.nonepileptic_seizure_unknown_onset = validated_data.get(
                "nonepileptic_seizure_unknown_onset",
                instance.nonepileptic_seizure_unknown_onset,
            )
            instance.nonepileptic_seizure_syncope = validated_data.get(
                "nonepileptic_seizure_syncope", instance.nonepileptic_seizure_syncope
            )
            instance.nonepileptic_seizure_behavioural = validated_data.get(
                "nonepileptic_seizure_behavioural",
                instance.nonepileptic_seizure_behavioural,
            )
            instance.nonepileptic_seizure_sleep = validated_data.get(
                "nonepileptic_seizure_sleep", instance.nonepileptic_seizure_sleep
            )
            instance.nonepileptic_seizure_paroxysmal = validated_data.get(
                "nonepileptic_seizure_paroxysmal",
                instance.nonepileptic_seizure_paroxysmal,
            )
            instance.nonepileptic_seizure_migraine = validated_data.get(
                "nonepileptic_seizure_migraine", instance.nonepileptic_seizure_migraine
            )
            instance.nonepileptic_seizure_miscellaneous = validated_data.get(
                "nonepileptic_seizure_miscellaneous",
                instance.nonepileptic_seizure_miscellaneous,
            )
            instance.nonepileptic_seizure_other = validated_data.get(
                "nonepileptic_seizure_other", instance.nonepileptic_seizure_other
            )
            instance.multiaxial_diagnosis = validated_data(
                "multiaxial_diagnosis", instance.multiaxial_diagnosis
            )

            instance.save()
            update_audit_progress(instance)
            calculate_kpis(instance.registration)
            return instance

    def create(self, validated_data):
        """
        create an episode
        """
        nhs_number = self.context.get("nhs_number")
        try:
            case = Case.objects.get(nhs_number=nhs_number)
        except Exception as error:
            raise serializers.ValidationError({"create episode": error})
        instance = Episode.objects.create(
            multiaxial_diagnosis=case.registration.multiaxialdiagnosis,
            seizure_onset_date=validated_data["seizure_onset_date"],
            seizure_onset_date_confidence=validated_data[
                "seizure_onset_date_confidence"
            ],
            episode_definition=validated_data["episode_definition"],
            has_description_of_the_episode_or_episodes_been_gathered=validated_data[
                "has_description_of_the_episode_or_episodes_been_gathered"
            ],
            description=validated_data["description"],
            description_keywords=validated_data["description_keywords"],
            epilepsy_or_nonepilepsy_status=validated_data[
                "epilepsy_or_nonepilepsy_status"
            ],
            epileptic_seizure_onset_type=validated_data["epileptic_seizure_onset_type"],
            nonepileptic_seizure_type=validated_data["nonepileptic_seizure_type"],
            epileptic_generalised_onset=validated_data["epileptic_generalised_onset"],
            focal_onset_impaired_awareness=validated_data[
                "focal_onset_impaired_awareness"
            ],
            focal_onset_automatisms=validated_data["focal_onset_automatisms"],
            focal_onset_atonic=validated_data["focal_onset_atonic"],
            focal_onset_clonic=validated_data["focal_onset_clonic"],
            focal_onset_left=validated_data["focal_onset_left"],
            focal_onset_right=validated_data["focal_onset_right"],
            focal_onset_epileptic_spasms=validated_data["focal_onset_epileptic_spasms"],
            focal_onset_hyperkinetic=validated_data["focal_onset_hyperkinetic"],
            focal_onset_myoclonic=validated_data["focal_onset_myoclonic"],
            focal_onset_tonic=validated_data["focal_onset_tonic"],
            focal_onset_autonomic=validated_data["focal_onset_autonomic"],
            focal_onset_behavioural_arrest=validated_data[
                "focal_onset_behavioural_arrest"
            ],
            focal_onset_cognitive=validated_data["focal_onset_cognitive"],
            focal_onset_emotional=validated_data["focal_onset_emotional"],
            focal_onset_sensory=validated_data["focal_onset_sensory"],
            focal_onset_centrotemporal=validated_data["focal_onset_centrotemporal"],
            focal_onset_temporal=validated_data["focal_onset_temporal"],
            focal_onset_frontal=validated_data["focal_onset_frontal"],
            focal_onset_parietal=validated_data["focal_onset_parietal"],
            focal_onset_occipital=validated_data["focal_onset_occipital"],
            focal_onset_gelastic=validated_data["focal_onset_gelastic"],
            focal_onset_focal_to_bilateral_tonic_clonic=validated_data[
                "focal_onset_focal_to_bilateral_tonic_clonic"
            ],
            nonepileptic_seizure_unknown_onset=validated_data[
                "nonepileptic_seizure_unknown_onset"
            ],
            nonepileptic_seizure_syncope=validated_data["nonepileptic_seizure_syncope"],
            nonepileptic_seizure_behavioural=validated_data[
                "nonepileptic_seizure_behavioural"
            ],
            nonepileptic_seizure_sleep=validated_data["nonepileptic_seizure_sleep"],
            nonepileptic_seizure_paroxysmal=validated_data[
                "nonepileptic_seizure_paroxysmal"
            ],
            nonepileptic_seizure_migraine=validated_data[
                "nonepileptic_seizure_migraine"
            ],
            nonepileptic_seizure_miscellaneous=validated_data[
                "nonepileptic_seizure_miscellaneous"
            ],
            nonepileptic_seizure_other=validated_data["nonepileptic_seizure_other"],
        )

        update_audit_progress(case.registration)
        calculate_kpis(case.registration)
        return instance
