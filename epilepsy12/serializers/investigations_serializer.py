# Python imports
from datetime import datetime

# Django imports


# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import Registration, Investigations
from epilepsy12.common_view_functions import update_audit_progress, calculate_kpis


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
            "eeg_wait",
            "twelve_lead_ecg_status",
            "ct_head_scan_status",
            "mri_indicated",
            "mri_brain_requested_date",
            "mri_brain_reported_date",
            "mri_wait",
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
