from datetime import datetime
from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework.views import APIView
from .models import *

# AuditProgress model here not included as only relevant to the Epilepsy12 app


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


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class CaseSerializer(serializers.HyperlinkedModelSerializer):
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


class RegistrationSerializer(serializers.HyperlinkedModelSerializer):
    registration_close_date = serializers.DateField(read_only=True)
    cohort = serializers.IntegerField(read_only=True)
    registration_date = serializers.DateField(validators=[is_future_date])
    eligibility_criteria_met = serializers.BooleanField(
        required=True, validators=[is_true]
    )
    child_name = serializers.CharField(source="case", required=False)

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
            "child_name",
        ]


class AuditProgressSerializer(serializers.HyperlinkedModelSerializer):
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
        ]


class CaseSerializer(serializers.HyperlinkedModelSerializer):
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


class FirstPaediatricAssessmentSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source="registration.case", required=False)

    class Meta:
        model = FirstPaediatricAssessment
        registration = serializers.PrimaryKeyRelatedField(
            queryset=Registration.objects.all()
        )
        audit_progress = serializers.PrimaryKeyRelatedField(
            queryset=AuditProgress.objects.all()
        )
        fields = [
            "id",
            "first_paediatric_assessment_in_acute_or_nonacute_setting",
            "has_number_of_episodes_since_the_first_been_documented",
            "general_examination_performed",
            "neurological_examination_performed",
            "developmental_learning_or_schooling_problems",
            "behavioural_or_emotional_problems",
            "child_name",
        ]


class MultiaxialDiagnosisSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MultiaxialDiagnosis
        registration = serializers.PrimaryKeyRelatedField(
            queryset=Registration.objects.all()
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
        ]


class EpisodeSerializer(serializers.HyperlinkedModelSerializer):
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


class SyndromeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Syndrome
        multiaxial_diagnosis = serializers.PrimaryKeyRelatedField(
            queryset=MultiaxialDiagnosis.objects.all()
        )
        fields = ["syndrome_diagnosis_date", "syndrome"]


class ComorbiditySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comorbidity
        multiaxial_diagnosis = serializers.PrimaryKeyRelatedField(
            queryset=MultiaxialDiagnosis.objects.all()
        )
        fields = ["comorbidity_diagnosis_date", "comorbidityentity"]


class InvestigationsSerializer(serializers.HyperlinkedModelSerializer):
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
            "mri_wait",
            "eeg_wait",
        ]


class AssessmentSerializer(serializers.HyperlinkedModelSerializer):
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
        ]


class ManagementSerializer(serializers.HyperlinkedModelSerializer):
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


class AntiEpilepsyMedicineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AntiEpilepsyMedicine
        management = serializers.PrimaryKeyRelatedField(
            queryset=Management.objects.all()
        )
        fields = [
            "medicine_id",
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


class SiteSerializer(serializers.HyperlinkedModelSerializer):
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


class OrganisationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organisation
        fields = [
            "OrganisationID",
            "OrganisationCode",
            "OrganisationType",
            "SubType",
            "Sector",
            "OrganisationStatus",
            "IsPimsManaged",
            "OrganisationName",
            "Address1",
            "Address2",
            "Address3",
            "City",
            "County",
            "Postcode",
            "Latitude",
            "Longitude",
            "ParentODSCode",
            "ParentName",
            "Phone",
            "Email",
            "Website",
            "Fax",
        ]


class KeywordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Keyword
        fields = ["keyword", "category"]
