# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import KPI


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
