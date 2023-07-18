# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import Assessment, Registration, Site, Organisation
from epilepsy12.common_view_functions import update_audit_progress, calculate_kpis


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
        ]

        def validate(self, data):
            if data["consultant_paediatrician_referral_made"]:
                if self.context("general_paediatric_centre_ods_code") is None:
                    raise serializers.ValidationError(
                        {
                            "Assessment": "General paediatric centre ODS code not provided. Assessment not saved."
                        }
                    )
                self.validate_two_dates(
                    self.data["consultant_paediatrician_referral_date"],
                    self.data["consultant_paediatrician_input_date"],
                )
            if data["paediatric_neurologist_referral_made"]:
                if self.context("paediatric_neurology_centre_ods_code") is None:
                    raise serializers.ValidationError(
                        {
                            "Assessment": "Paediatric neurology centre ODS code not provided. Assessment not saved."
                        }
                    )
                self.validate_two_dates(
                    data["paediatric_neurologist_referral_date"],
                    self.data["paediatric_neurologist_input_date"],
                )
            if data["childrens_epilepsy_surgical_service_referral_made"]:
                if self.context("epilepsy_surgery_centre_ods_code") is None:
                    raise serializers.ValidationError(
                        {
                            "Assessment": "Children's epilepsy surgery centre ODS code not provided. Assessment not saved."
                        }
                    )
                self.validate_two_dates(
                    self.data["childrens_epilepsy_surgical_service_referral_date"],
                    self.data["childrens_epilepsy_surgical_service_input_date"],
                )

        def validate_two_dates(date1, date2):
            """
            class method - ensures both dates are present and date1 is before date2
            """
            if date1 is None or date2 is None:
                raise serializers.ValidationError(
                    {
                        "Assessment": "Referral or input date(s) not provided. Assessment not saved."
                    }
                )
            if date1 > date2:
                raise serializers.ValidationError(
                    {
                        "Assessment": "Referral date cannot be after input date(s). Assessment not saved."
                    }
                )

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

            if (
                instance.consultant_paediatrician_referral_made
                or instance.paediatric_neurologist_referral_made
                or instance.childrens_epilepsy_surgical_service_referral_made
            ):
                if instance.consultant_paediatrician_referral_made:
                    if (
                        Site.objects.filter(
                            case=instance.registration.case,
                            site_is_actively_involved_in_epilepsy_care=True,
                            organisation__ODSCode=self.context[
                                "general_paediatric_centre_ods_code"
                            ],
                        ).count()
                        > 0
                    ):
                        site = Site.objects.filter(
                            case=instance.registration.case,
                            site_is_actively_involved_in_epilepsy_care=True,
                            organisation__ODSCode=self.context[
                                "general_paediatric_centre_ods_code"
                            ],
                        ).get()
                        site.site_is_general_paediatric_centre = True
                        site.save()
                    else:
                        organisation = Organisation.objects.get(
                            ODSCode=self.context["general_paediatric_centre_ods_code"]
                        )
                        Site.objects.create(
                            case=instance.registration.case,
                            site_is_actively_involved_in_epilepsy_care=True,
                            site_is_general_paediatric_centre=True,
                            organisation=organisation,
                        )
                if instance.paediatric_neurologist_referral_made:
                    if (
                        Site.objects.filter(
                            case=instance.registration.case,
                            site_is_actively_involved_in_epilepsy_care=True,
                            organisation__ODSCode=self.context[
                                "paediatric_neurology_centre_ods_code"
                            ],
                        ).count()
                        > 0
                    ):
                        site = Site.objects.filter(
                            case=instance.registration.case,
                            site_is_actively_involved_in_epilepsy_care=True,
                            organisation__ODSCode=self.context[
                                "paediatric_neurology_centre_ods_code"
                            ],
                        ).get()
                        site.site_is_paediatric_neurology_centre = True
                        site.save()
                    else:
                        organisation = Organisation.objects.get(
                            ODSCode=self.context["general_paediatric_centre_ods_code"]
                        )
                        Site.objects.create(
                            case=instance.registration.case,
                            site_is_actively_involved_in_epilepsy_care=True,
                            site_is_paediatric_neurology_centre=True,
                            organisation=organisation,
                        )
                if instance.childrens_epilepsy_surgical_service_referral_made:
                    if (
                        Site.objects.filter(
                            case=instance.registration.case,
                            site_is_actively_involved_in_epilepsy_care=True,
                            organisation__ODSCode=self.context[
                                "epilepsy_surgery_centre_ods_code"
                            ],
                        ).count()
                        > 0
                    ):
                        site = Site.objects.filter(
                            case=instance.registration.case,
                            site_is_actively_involved_in_epilepsy_care=True,
                            organisation__ODSCode=self.context[
                                "epilepsy_surgery_centre_ods_code"
                            ],
                        ).get()
                        site.site_is_childrens_epilepsy_surgery_centre = True
                        site.save()
                    else:
                        organisation = Organisation.objects.get(
                            ODSCode=self.context["general_paediatric_centre_ods_code"]
                        )
                        Site.objects.create(
                            case=instance.registration.case,
                            site_is_actively_involved_in_epilepsy_care=True,
                            site_is_paediatric_neurology_centre=True,
                            organisation=organisation,
                        )

            update_audit_progress(instance)
            calculate_kpis(instance.registration)
            return instance
