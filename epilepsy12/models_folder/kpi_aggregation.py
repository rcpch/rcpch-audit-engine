from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from .help_text_mixin import HelpTextMixin

# RCPCH imports


class BaseKPIAggregation(models.Model, HelpTextMixin):
    """
    KPI summary statistics.
    """

    open_access = models.BooleanField(default=False, null=True, blank=True)

    paediatrician_with_expertise_in_epilepsies_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    paediatrician_with_expertise_in_epilepsies_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    paediatrician_with_expertise_in_epilepsies_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    paediatrician_with_expertise_in_epilepsies_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    epilepsy_specialist_nurse_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    epilepsy_specialist_nurse_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    epilepsy_specialist_nurse_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    epilepsy_specialist_nurse_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    tertiary_input_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    tertiary_input_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    tertiary_input_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    tertiary_input_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    epilepsy_surgery_referral_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    epilepsy_surgery_referral_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    epilepsy_surgery_referral_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    epilepsy_surgery_referral_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    ecg_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    ecg_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    ecg_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    ecg_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    mri_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    mri_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    mri_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    mri_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    assessment_of_mental_health_issues_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    assessment_of_mental_health_issues_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    assessment_of_mental_health_issues_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    assessment_of_mental_health_issues_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    mental_health_support_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    mental_health_support_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    mental_health_support_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    mental_health_support_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    sodium_valproate_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    sodium_valproate_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    sodium_valproate_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    sodium_valproate_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    comprehensive_care_planning_agreement_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    comprehensive_care_planning_agreement_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    comprehensive_care_planning_agreement_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    comprehensive_care_planning_agreement_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    patient_held_individualised_epilepsy_document_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    patient_held_individualised_epilepsy_document_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    patient_held_individualised_epilepsy_document_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    patient_held_individualised_epilepsy_document_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    patient_carer_parent_agreement_to_the_care_planning_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    patient_carer_parent_agreement_to_the_care_planning_total_eligible = (
        models.IntegerField(
            help_text={"label": "", "reference": ""},
            null=True,
            default=None,
            db_column="pt_carer_parent_agree_care_place_total_eligible",
        )
    )
    patient_carer_parent_agreement_to_the_care_planning_ineligible = (
        models.IntegerField(
            help_text={"label": "", "reference": ""},
            null=True,
            default=None,
        )
    )
    patient_carer_parent_agreement_to_the_care_planning_incomplete = (
        models.IntegerField(
            help_text={"label": "", "reference": ""},
            null=True,
            default=None,
        )
    )

    care_planning_has_been_updated_when_necessary_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    care_planning_has_been_updated_when_necessary_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    care_planning_has_been_updated_when_necessary_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    care_planning_has_been_updated_when_necessary_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    comprehensive_care_planning_content_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    comprehensive_care_planning_content_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    comprehensive_care_planning_content_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    comprehensive_care_planning_content_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    parental_prolonged_seizures_care_plan_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    parental_prolonged_seizures_care_plan_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    parental_prolonged_seizures_care_plan_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    parental_prolonged_seizures_care_plan_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    water_safety_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    water_safety_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    water_safety_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    water_safety_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    first_aid_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    first_aid_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    first_aid_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    first_aid_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    general_participation_and_risk_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    general_participation_and_risk_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    general_participation_and_risk_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    general_participation_and_risk_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    service_contact_details_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    service_contact_details_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    service_contact_details_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    service_contact_details_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    sudep_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    sudep_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    sudep_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    sudep_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    school_individual_healthcare_plan_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    school_individual_healthcare_plan_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    school_individual_healthcare_plan_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )
    school_individual_healthcare_plan_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
        null=True,
        default=None,
    )

    last_updated = models.DateTimeField(
        help_text={"label": "", "reference": ""},
        auto_now=True,
    )

    class Meta:
        abstract = True
        verbose_name = _("Base KPI Aggregation Model")
        verbose_name_plural = _("Base KPI Aggregation Models")

    def __str__(self):
        return f"Base KPI aggregation result model"


class OrganisationKPIAggregation(BaseKPIAggregation):
    """
    KPI summary statistics for organisations.
    """

    # Define relationships
    organisation = models.ForeignKey(
        to="epilepsy12.Organisation",
        on_delete=models.CASCADE,
    )


class TrustKPIAggregation(BaseKPIAggregation):
    """
    KPI summary statistics for organisations.
    """

    # Define relationships
    parent_organisation_ods_code = models.CharField(max_length=100)
