# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import Case, Organisation, Site
from epilepsy12.common_view_functions import update_audit_progress, calculate_kpis


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
