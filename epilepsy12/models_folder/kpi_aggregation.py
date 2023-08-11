from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from .help_text_mixin import HelpTextMixin

# RCPCH imports


class KPIAggregation(models.Model, HelpTextMixin):
    """
    KPI summary statistics.
    
    Each model instance is associated with a single organisation.
    """

    open_access = models.BooleanField(default=False, null=True, blank=True)

    paediatrician_with_expertise_in_epilepsies_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    paediatrician_with_expertise_in_epilepsies_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    paediatrician_with_expertise_in_epilepsies_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    paediatrician_with_expertise_in_epilepsies_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    epilepsy_specialist_nurse_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    epilepsy_specialist_nurse_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    epilepsy_specialist_nurse_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    epilepsy_specialist_nurse_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    tertiary_input_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    tertiary_input_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    tertiary_input_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    tertiary_input_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    epilepsy_surgery_referral_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    epilepsy_surgery_referral_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    epilepsy_surgery_referral_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    epilepsy_surgery_referral_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    ecg_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    ecg_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    ecg_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    ecg_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    mri_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    mri_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    mri_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    mri_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    assessment_of_mental_health_issues_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    assessment_of_mental_health_issues_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    assessment_of_mental_health_issues_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    assessment_of_mental_health_issues_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    mental_health_support_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    mental_health_support_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    mental_health_support_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    mental_health_support_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    sodium_valproate_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    sodium_valproate_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    sodium_valproate_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    sodium_valproate_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    comprehensive_care_planning_agreement_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    comprehensive_care_planning_agreement_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    comprehensive_care_planning_agreement_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    comprehensive_care_planning_agreement_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    patient_held_individualised_epilepsy_document_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    patient_held_individualised_epilepsy_document_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    patient_held_individualised_epilepsy_document_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    patient_held_individualised_epilepsy_document_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    patient_carer_parent_agreement_to_the_care_planning_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    patient_carer_parent_agreement_to_the_care_planning_total_eligible = (
        models.IntegerField(
            help_text={"label": "", "reference": ""},
            db_column='pt_carer_parent_agree_care_place_total_eligible'
        )
    )
    patient_carer_parent_agreement_to_the_care_planning_ineligible = (
        models.IntegerField(
            help_text={"label": "", "reference": ""},
        )
    )
    patient_carer_parent_agreement_to_the_care_planning_incomplete = (
        models.IntegerField(
            help_text={"label": "", "reference": ""},
        )
    )

    care_planning_has_been_updated_when_necessary_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    care_planning_has_been_updated_when_necessary_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    care_planning_has_been_updated_when_necessary_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    care_planning_has_been_updated_when_necessary_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    comprehensive_care_planning_content_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    comprehensive_care_planning_content_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    comprehensive_care_planning_content_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    comprehensive_care_planning_content_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    parental_prolonged_seizures_care_plan_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    parental_prolonged_seizures_care_plan_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    parental_prolonged_seizures_care_plan_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    parental_prolonged_seizures_care_plan_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    water_safety_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    water_safety_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    water_safety_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    water_safety_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    first_aid_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    first_aid_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    first_aid_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    first_aid_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    general_participation_and_risk_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    general_participation_and_risk_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    general_participation_and_risk_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    general_participation_and_risk_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    service_contact_details_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    service_contact_details_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    service_contact_details_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    service_contact_details_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    sudep_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    sudep_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    sudep_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    sudep_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )

    school_individual_healthcare_plan_passed = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    school_individual_healthcare_plan_total_eligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    school_individual_healthcare_plan_ineligible = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    school_individual_healthcare_plan_incomplete = models.IntegerField(
        help_text={"label": "", "reference": ""},
    )
    
    last_updated = models.DateTimeField(
        help_text={"label": "", "reference": ""},
        auto_now=True,
    )

    # Define relationships
    organisation = models.ForeignKey(
        to="epilepsy12.Organisation",
        blank=True,
        default=None,
        null=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("KPI Aggregation Result")
        verbose_name_plural = _("KPI Aggregation Results")

    def __str__(self):
        return f"KPI aggregation results for {self.organisation.OrganisationName}"
