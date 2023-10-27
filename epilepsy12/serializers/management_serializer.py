# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import Management, Registration
from epilepsy12.common_view_functions import update_audit_progress, calculate_kpis


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
