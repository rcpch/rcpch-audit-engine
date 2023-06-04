from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from .help_text_mixin import HelpTextMixin

# RCPCH imports
from ..constants import ABSTRACTION_LEVELS


class KPIAggregation(models.Model, HelpTextMixin):
    """
    KPI summary statistics
    Model is updated each time a new case is registered and fully scored
    There is an instance of KPI_Aggregation for each organisation each level of abstraction ('organisation', 'trust', 'icb', 'open_uk', 'nhs_region', 'country', 'national')
    """

    paediatrician_with_expertise_in_epilepsies = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    paediatrician_with_expertise_in_epilepsies_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    paediatrician_with_expertise_in_epilepsies_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    epilepsy_specialist_nurse = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    epilepsy_specialist_nurse_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    epilepsy_specialist_nurse_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    tertiary_input = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    tertiary_input_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    tertiary_input_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    epilepsy_surgery_referral = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    epilepsy_surgery_referral_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    epilepsy_surgery_referral_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    ecg = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    ecg_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    ecg_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    mri = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    mri_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    mri_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    assessment_of_mental_health_issues = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    assessment_of_mental_health_issues_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    assessment_of_mental_health_issues_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    mental_health_support = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    mental_health_support_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    mental_health_support_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    sodium_valproate = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    sodium_valproate_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    sodium_valproate_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    comprehensive_care_planning_agreement = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    comprehensive_care_planning_agreement_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    comprehensive_care_planning_agreement_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    patient_held_individualised_epilepsy_document = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    patient_held_individualised_epilepsy_document_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    patient_held_individualised_epilepsy_document_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    patient_carer_parent_agreement_to_the_care_planning = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    patient_carer_parent_agreement_to_the_care_planning_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    patient_carer_parent_agreement_to_the_care_planning_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    care_planning_has_been_updated_when_necessary = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    care_planning_has_been_updated_when_necessary_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    care_planning_has_been_updated_when_necessary_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    comprehensive_care_planning_content = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    comprehensive_care_planning_content_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    comprehensive_care_planning_content_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    parental_prolonged_seizures_care_plan = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    parental_prolonged_seizures_care_plan_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    parental_prolonged_seizures_care_plan_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    water_safety = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    water_safety_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    water_safety_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    first_aid = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    first_aid_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    first_aid_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    general_participation_and_risk = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    general_participation_and_risk_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    general_participation_and_risk_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    service_contact_details = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    service_contact_details_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    service_contact_details_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    sudep = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    sudep_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    sudep_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    school_individual_healthcare_plan = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    school_individual_healthcare_plan_average = models.FloatField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    school_individual_healthcare_plan_total = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    total_number_of_cases = models.IntegerField(
        help_text={"label": "", "reference": ""},
        default=None,
        null=True,
        blank=True,
    )
    abstraction_level = models.CharField(
        choices=ABSTRACTION_LEVELS,
        max_length=50,
    )

    open_access = models.BooleanField(default=False, null=True, blank=True)

    organisation = models.ForeignKey(
        to="epilepsy12.Organisation",
        blank=True,
        default=None,
        null=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("KPI Aggregation Result ")
        verbose_name_plural = _("KPI Aggregation Results ")

    def __str__(self):
        return f"KPI aggregation results for child in {self.organisation.OrganisationName}({self.organisation.ParentOrganisation_OrganisationName})"
