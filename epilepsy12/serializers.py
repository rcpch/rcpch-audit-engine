# Python imports
from datetime import datetime

# Django imports
from django.contrib.auth.models import Group

# DRF imports
from rest_framework import serializers

# E12 imports
from .models import *
from .common_view_functions import update_audit_progress, calculate_kpis


class NestedCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ["id", "first_name", "surname", "nhs_number"]


class Epilepsy12UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Epilepsy12User
        fields = [
            "first_name",
            "surname",
            "title",
            "email",
            "username",
            "is_active",
            "is_staff",
            "is_rcpch_staff",
            "is_superuser",
            "is_rcpch_audit_team_member",
            "view_preference",
            "date_joined",
            "role",
        ]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = [
            "locked",
            "locked_at",
            "locked_by",
            "nhs_number",
            "first_name",
            "surname",
            "sex",
            "date_of_birth",
            "postcode",
            "ethnicity",
            "index_of_multiple_deprivation_quintile",
            "organisations",
        ]


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


class AuditProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditProgress
        fields = "__all__"


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
            "registration",
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


class FirstPaediatricAssessmentSerializer(serializers.ModelSerializer):
    # case = serializers.CharField(source="registration.case", required=False)
    # nhs_number = serializers.CharField(
    #     source="registration.case.nhs_number", required=True
    # )

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
            "registration",
            # "nhs_number",
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


class EpilepsyCauseEntitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EpilepsyCauseEntity
        fields = "__all__"


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

            instance.save()
            update_audit_progress(instance)
            calculate_kpis(instance.registration)
            return instance


class SyndromeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Syndrome
        multiaxial_diagnosis = serializers.PrimaryKeyRelatedField(
            queryset=MultiaxialDiagnosis.objects.all()
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


class ComorbiditySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comorbidity
        multiaxial_diagnosis = serializers.PrimaryKeyRelatedField(
            queryset=MultiaxialDiagnosis.objects.all()
        )
        fields = ["comorbidity_diagnosis_date", "comorbidityentity"]

        def update(self, instance, validated_data):
            instance.comorbidity_diagnosis_date = validated_data.get(
                "comorbidity_diagnosis_date", instance.comorbidity_diagnosis_date
            )
            instance.comorbidityentity = validated_data.get(
                "comorbidityentity", instance.comorbidityentity
            )

            instance.save()
            update_audit_progress(instance)
            calculate_kpis(instance.registration)
            return instance


class MultiaxialDiagnosisSerializer(serializers.ModelSerializer):
    episodes = EpisodeSerializer(many=True, read_only=True)
    syndromes = SyndromeSerializer(many=True, read_only=True)
    comorbidities = SyndromeSerializer(many=True, read_only=True)

    class Meta:
        model = MultiaxialDiagnosis
        registration = serializers.PrimaryKeyRelatedField(
            queryset=Registration.objects.all()
        )
        epilepsy_cause = serializers.SlugRelatedField(
            queryset=EpilepsyCauseEntity.objects.all(),
            slug_field="preferredTerm",
        )

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
        ]

    # def get_epilepsy_cause(self, obj):
    def get_epilepsy_cause(self):
        """
        This is a custom method as the user passes in an SCTID of the epilepsy cause
        This is validated and used to look up the value in the the EpilepsyCauseEntity table
        and passed back to the epilepsy_cause field in the Multiaxial Diagnosis instance in the save()
        """
        sctid = self.context.get("sctid")
        if sctid is not None:
            if EpilepsyCauseEntity.objects.filter(conceptId=sctid).exists():
                self.instance.epilepsy_cause = EpilepsyCauseEntity.objects.filter(
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
        instance.syndrome_present = validated_data.get(
            "syndrome_present", instance.syndrome_present
        )
        instance.epilepsy_cause_known = validated_data.get(
            "epilepsy_cause_known", instance.epilepsy_cause_known
        )

        instance.epilepsy_cause_categories = validated_data.get(
            "epilepsy_cause_categories", instance.epilepsy_cause_categories
        )
        instance.relevant_impairments_behavioural_educational = validated_data.get(
            "relevant_impairments_behavioural_educational",
            instance.relevant_impairments_behavioural_educational,
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


class InvestigationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investigations
        registration = serializers.PrimaryKeyRelatedField(
            queryset=Registration.objects.all()
        )
        fields = [
            "eeg_indicated",
            "eeg_request_date",
            "eeg_performed_date",
            "twelve_lead_ecg_status",
            "ct_head_scan_status",
            "mri_indicated",
            "mri_brain_requested_date",
            "mri_brain_reported_date",
        ]

        def update(self, instance, validated_data):
            instance.eeg_indicated = validated_data.get(
                "eeg_indicated", instance.eeg_indicated
            )
            instance.eeg_request_date = validated_data.get(
                "eeg_request_date", instance.eeg_request_date
            )
            instance.eeg_performed_date = validated_data.get(
                "eeg_performed_date", instance.eeg_performed_date
            )
            instance.twelve_lead_ecg_status = validated_data.get(
                "twelve_lead_ecg_status", instance.twelve_lead_ecg_status
            )
            instance.ct_head_scan_status = validated_data.get(
                "ct_head_scan_status", instance.ct_head_scan_status
            )
            instance.mri_indicated = validated_data.get(
                "mri_indicated", instance.mri_indicated
            )
            instance.mri_brain_requested_date = validated_data.get(
                "mri_brain_requested_date", instance.mri_brain_requested_date
            )
            instance.mri_brain_reported_date = validated_data.get(
                "mri_brain_reported_date", instance.mri_brain_reported_date
            )

            instance.save()
            update_audit_progress(instance)
            calculate_kpis(instance.registration)
            return instance


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        registration = serializers.PrimaryKeyRelatedField(
            queryset=Registration.objects.all()
        )
        fields = [
            "childrens_epilepsy_surgical_service_referral_criteria_met",
            "consultant_paediatrician_referral_made",
            "consultant_paediatrician_referral_date",
            "consultant_paediatrician_input_date",
            "paediatric_neurologist_referral_made",
            "paediatric_neurologist_referral_date",
            "paediatric_neurologist_input_date",
            "childrens_epilepsy_surgical_service_referral_made",
            "childrens_epilepsy_surgical_service_referral_date",
            "childrens_epilepsy_surgical_service_input_date",
            "epilepsy_specialist_nurse_referral_made",
            "epilepsy_specialist_nurse_referral_date",
            "epilepsy_specialist_nurse_input_date",
            "case",
        ]

        def update(self, instance, validated_data):
            instance.childrens_epilepsy_surgical_service_referral_criteria_met = (
                validated_data.get(
                    "childrens_epilepsy_surgical_service_referral_criteria_met",
                    instance.childrens_epilepsy_surgical_service_referral_criteria_met,
                )
            )
            instance.consultant_paediatrician_referral_made = validated_data.get(
                "consultant_paediatrician_referral_made",
                instance.consultant_paediatrician_referral_made,
            )
            instance.consultant_paediatrician_referral_date = validated_data.get(
                "consultant_paediatrician_referral_date",
                instance.consultant_paediatrician_referral_date,
            )
            instance.consultant_paediatrician_input_date = validated_data.get(
                "consultant_paediatrician_input_date",
                instance.consultant_paediatrician_input_date,
            )
            instance.paediatric_neurologist_referral_made = validated_data.get(
                "paediatric_neurologist_referral_made",
                instance.paediatric_neurologist_referral_made,
            )
            instance.paediatric_neurologist_referral_date = validated_data.get(
                "paediatric_neurologist_referral_date",
                instance.paediatric_neurologist_referral_date,
            )
            instance.paediatric_neurologist_input_date = validated_data.get(
                "paediatric_neurologist_input_date",
                instance.paediatric_neurologist_input_date,
            )
            instance.childrens_epilepsy_surgical_service_referral_made = (
                validated_data.get(
                    "childrens_epilepsy_surgical_service_referral_made",
                    instance.childrens_epilepsy_surgical_service_referral_made,
                )
            )
            instance.childrens_epilepsy_surgical_service_referral_date = (
                validated_data.get(
                    "childrens_epilepsy_surgical_service_referral_date",
                    instance.childrens_epilepsy_surgical_service_referral_date,
                )
            )
            instance.childrens_epilepsy_surgical_service_input_date = (
                validated_data.get(
                    "childrens_epilepsy_surgical_service_input_date",
                    instance.childrens_epilepsy_surgical_service_input_date,
                )
            )
            instance.epilepsy_specialist_nurse_referral_made = validated_data.get(
                "epilepsy_specialist_nurse_referral_made",
                instance.epilepsy_specialist_nurse_referral_made,
            )
            instance.epilepsy_specialist_nurse_referral_date = validated_data.get(
                "epilepsy_specialist_nurse_referral_date",
                instance.epilepsy_specialist_nurse_referral_date,
            )
            instance.epilepsy_specialist_nurse_input_date = validated_data.get(
                "epilepsy_specialist_nurse_input_date",
                instance.epilepsy_specialist_nurse_input_date,
            )
            instance.save()
            update_audit_progress(instance)
            calculate_kpis(instance.registration)
            return instance


class ManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Management
        registration = serializers.PrimaryKeyRelatedField(
            queryset=Registration.objects.all()
        )
        fields = [
            "has_an_aed_been_given",
            "has_rescue_medication_been_prescribed",
            "individualised_care_plan_in_place",
            "individualised_care_plan_date",
            "individualised_care_plan_has_parent_carer_child_agreement",
            "individualised_care_plan_includes_service_contact_details",
            "individualised_care_plan_include_first_aid",
            "individualised_care_plan_parental_prolonged_seizure_care",
            "individualised_care_plan_includes_general_participation_risk",
            "individualised_care_plan_addresses_water_safety",
            "individualised_care_plan_addresses_sudep",
            "individualised_care_plan_includes_ehcp",
            "has_individualised_care_plan_been_updated_in_the_last_year",
            "has_been_referred_for_mental_health_support",
            "has_support_for_mental_health_support",
        ]

        def update(self, instance, validated_data):
            instance.has_an_aed_been_given = validated_data.get(
                "has_an_aed_been_given", instance.has_an_aed_been_given
            )
            instance.has_rescue_medication_been_prescribed = validated_data.get(
                "has_rescue_medication_been_prescribed",
                instance.has_rescue_medication_been_prescribed,
            )
            instance.individualised_care_plan_in_place = validated_data.get(
                "individualised_care_plan_in_place",
                instance.individualised_care_plan_in_place,
            )
            instance.individualised_care_plan_date = validated_data.get(
                "individualised_care_plan_date", instance.individualised_care_plan_date
            )
            instance.individualised_care_plan_has_parent_carer_child_agreement = (
                validated_data.get(
                    "individualised_care_plan_has_parent_carer_child_agreement",
                    instance.individualised_care_plan_has_parent_carer_child_agreement,
                )
            )
            instance.individualised_care_plan_includes_service_contact_details = (
                validated_data.get(
                    "individualised_care_plan_includes_service_contact_details",
                    instance.individualised_care_plan_includes_service_contact_details,
                )
            )
            instance.individualised_care_plan_include_first_aid = validated_data.get(
                "individualised_care_plan_include_first_aid",
                instance.individualised_care_plan_include_first_aid,
            )
            instance.individualised_care_plan_parental_prolonged_seizure_care = (
                validated_data.get(
                    "individualised_care_plan_parental_prolonged_seizure_care",
                    instance.individualised_care_plan_parental_prolonged_seizure_care,
                )
            )
            instance.individualised_care_plan_includes_general_participation_risk = validated_data.get(
                "individualised_care_plan_includes_general_participation_risk",
                instance.individualised_care_plan_includes_general_participation_risk,
            )
            instance.individualised_care_plan_addresses_water_safety = (
                validated_data.get(
                    "individualised_care_plan_addresses_water_safety",
                    instance.individualised_care_plan_addresses_water_safety,
                )
            )
            instance.individualised_care_plan_addresses_sudep = validated_data.get(
                "individualised_care_plan_addresses_sudep",
                instance.individualised_care_plan_addresses_sudep,
            )
            instance.individualised_care_plan_includes_ehcp = validated_data.get(
                "individualised_care_plan_includes_ehcp",
                instance.individualised_care_plan_includes_ehcp,
            )
            instance.has_individualised_care_plan_been_updated_in_the_last_year = (
                validated_data.get(
                    "has_individualised_care_plan_been_updated_in_the_last_year",
                    instance.has_individualised_care_plan_been_updated_in_the_last_year,
                )
            )
            instance.has_been_referred_for_mental_health_support = validated_data.get(
                "has_been_referred_for_mental_health_support",
                instance.has_been_referred_for_mental_health_support,
            )
            instance.has_support_for_mental_health_support = validated_data.get(
                "has_support_for_mental_health_support",
                instance.has_support_for_mental_health_support,
            )

            instance.save()
            update_audit_progress(instance)
            calculate_kpis(instance.registration)
            return instance


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


class SiteSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source="case")

    class Meta:
        model = Site
        case = serializers.PrimaryKeyRelatedField(queryset=Case.objects.all())
        organisation = serializers.PrimaryKeyRelatedField(
            queryset=Organisation.objects.all()
        )
        fields = [
            "site_is_actively_involved_in_epilepsy_care",
            "site_is_primary_centre_of_epilepsy_care",
            "site_is_childrens_epilepsy_surgery_centre",
            "site_is_paediatric_neurology_centre",
            "site_is_general_paediatric_centre",
            "case",
            "organisation",
            "child_name",
        ]

        def update(self, instance, validated_data):
            instance.site_is_actively_involved_in_epilepsy_care = validated_data.get(
                "site_is_actively_involved_in_epilepsy_care",
                instance.site_is_actively_involved_in_epilepsy_care,
            )
            instance.site_is_primary_centre_of_epilepsy_care = validated_data.get(
                "site_is_primary_centre_of_epilepsy_care",
                instance.site_is_primary_centre_of_epilepsy_care,
            )
            instance.site_is_childrens_epilepsy_surgery_centre = validated_data.get(
                "site_is_childrens_epilepsy_surgery_centre",
                instance.site_is_childrens_epilepsy_surgery_centre,
            )
            instance.site_is_paediatric_neurology_centre = validated_data.get(
                "site_is_paediatric_neurology_centre",
                instance.site_is_paediatric_neurology_centre,
            )
            instance.site_is_general_paediatric_centre = validated_data.get(
                "site_is_general_paediatric_centre",
                instance.site_is_general_paediatric_centre,
            )

            instance.save()
            update_audit_progress(instance)
            calculate_kpis(instance.registration)
            return instance


class OrganisationCaseSerializer(serializers.ModelSerializer):
    cases = CaseSerializer(many=True, read_only=True)

    class Meta:
        model = Organisation
        fields = [
            "ODSCode",
            "OrganisationName",
            "Website",
            "Address1",
            "Address2",
            "Address3",
            "City",
            "County",
            "Latitude",
            "Longitude",
            "Postcode",
            "Geocode_Coordinates",
            "ParentOrganisation_ODSCode",
            "ParentOrganisation_OrganisationName",
            "LastUpdatedDate",
            "cases",
        ]


class OrganisationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organisation
        fields = [
            "ODSCode",
            "OrganisationName",
            "Website",
            "Address1",
            "Address2",
            "Address3",
            "City",
            "County",
            "Latitude",
            "Longitude",
            "Postcode",
            "Geocode_Coordinates",
            "ParentOrganisation_ODSCode",
            "ParentOrganisation_OrganisationName",
            "LastUpdatedDate",
        ]


class KeyPerformanceIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = KPI
        fields = [
            "paediatrician_with_expertise_in_epilepsies",
            "epilepsy_specialist_nurse",
            "tertiary_input",
            "epilepsy_surgery_referral",
            "ecg",
            "mri",
            "assessment_of_mental_health_issues",
            "mental_health_support",
            "sodium_valproate",
            "comprehensive_care_planning_agreement",
            "patient_held_individualised_epilepsy_document",
            "patient_carer_parent_agreement_to_the_care_planning",
            "care_planning_has_been_updated_when_necessary",
            "comprehensive_care_planning_content",
            "parental_prolonged_seizures_care_plan",
            "water_safety",
            "first_aid",
            "general_participation_and_risk",
            "sudep",
            "service_contact_details",
            "school_individual_healthcare_plan",
            "organisation",
            "parent_trust",
        ]


class KeywordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Keyword
        fields = ["keyword", "category"]


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = [
            "locked",
            "locked_at",
            "locked_by",
            "nhs_number",
            "first_name",
            "surname",
            "sex",
            "date_of_birth",
            "postcode",
            "ethnicity",
            "index_of_multiple_deprivation_quintile",
        ]
