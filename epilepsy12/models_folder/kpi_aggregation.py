# TODO: an improvement refactor would be adding a 'get_abstraction_name' to the EnumAbstractionLevel Class, and then using that to save the .abstraction_name field for each of these models
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from .help_text_mixin import HelpTextMixin

# RCPCH imports
from epilepsy12.constants import EnumAbstractionLevel
from django.apps import apps


class BaseKPIMetrics(models.Model):
    """Base class containing only the metric fields themselves."""

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


class BaseKPIAggregation(BaseKPIMetrics, HelpTextMixin):
    """
    KPI summary statistics base class. Handles data and logic common to all aggregation models.

    Metric fields inherited from BaseKPIMetrics.
    """

    abstraction_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None,
    )

    # If True, this KPIAgg is available to access by public
    open_access = models.BooleanField(
        default=False,
    )

    last_updated = models.DateTimeField(
        help_text={"label": "", "reference": ""},
        auto_now=True,
    )

    cohort = models.PositiveSmallIntegerField(
        default=None,
    )

    # At the end of cohort, this flag will be made True, indicating the final aggregation for that cohort
    final_publication = models.BooleanField(
        default=False,
        null=False,
    )

    class Meta:
        abstract = True
        verbose_name = _("Base KPI Aggregation Model")
        verbose_name_plural = _("Base KPI Aggregation Models")

    def get_pct_passed_kpi(self, kpi_name: str) -> float:
        passed = getattr(self, f"{kpi_name}_passed")
        total = getattr(self, f"{kpi_name}_total_eligible")

        if total == 0:
            return None

        return passed / total

    def aggregation_performed(self) -> bool:
        """All fields should be updated at the same time. Therefore, if one field is None, all will be None -> aggregations are not performed."""
        if self.ecg_passed is None:
            return False
        else:
            return True

    def get_value_counts_for_kpis(self, kpis: list[str]) -> dict:
        """Getter for value count values. Accepts a list of kpi names as strings. For each KPI, will return the 4 associated value count fields, in a single combined dict."""
        all_value_counts = {}
        for kpi in kpis:
            for metric in ["passed", "total_eligible", "ineligible", "incomplete"]:
                kpi_metric = f"{kpi}_{metric}"
                value = getattr(self, kpi_metric)
                all_value_counts.update({kpi_metric: value})
        return all_value_counts

    def __str__(self):
        return f"Base KPI aggregation result model"


class OrganisationKPIAggregation(BaseKPIAggregation):
    """
    KPI summary statistics for organisations.
    """

    # Define relationships
    abstraction_relation = models.OneToOneField(
        to="epilepsy12.Organisation",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Organisation KPI Aggregation Model")
        verbose_name_plural = _("Organisation KPI Aggregation Models")

    def get_abstraction_level(self) -> str:
        return EnumAbstractionLevel.ORGANISATION

    def get_name(self) -> str:
        return f"{self.abstraction_name}"

    def __str__(self):
        return f"OrganisationKPIAggregation (ODSCode={self.abstraction_relation.ODSCode}) KPIAggregations"

    def save(self, *args, **kwargs) -> None:
        # UPDATE THE abstraction_name field
        if self.abstraction_relation is not None:
            self.abstraction_name = self.abstraction_relation.OrganisationName
        else:
            self.abstraction_name = "Name not found"
        return super().save(*args, **kwargs)


class TrustKPIAggregation(BaseKPIAggregation):
    """
    KPI summary statistics for Trusts.
    """

    # Define relationships
    # NOTE: parent_organisation_ods_code is not unique (multiple Organisation objects can share the same) so just store in a charfield
    abstraction_relation = models.CharField(
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = _("Trust KPI Aggregation Model")
        verbose_name_plural = _("Trust KPI Aggregation Models")

    def get_abstraction_level(self) -> str:
        return EnumAbstractionLevel.TRUST

    def get_name(self) -> str:
        return f"{self.abstraction_name}"

    def __str__(self):
        return f"TrustKPIAggregation (parent_organisation_ods_code={self.abstraction_relation})"

    def save(self, *args, **kwargs) -> None:
        # UPDATE THE abstraction_name field
        if self.abstraction_relation is not None:
            # As Trust is the only abstraction relation without a 1-2-1 model, need to search Org to get Trust name
            Organisation = apps.get_model("epilepsy12", "Organisation")

            organisation = Organisation.objects.filter(
                ParentOrganisation_ODSCode=self.abstraction_relation
            ).first()

            self.abstraction_name = organisation.ParentOrganisation_OrganisationName

        return super().save(*args, **kwargs)


class ICBKPIAggregation(BaseKPIAggregation):
    """
    KPI summary statistics for IntegratedCareBoard.
    """

    # Define relationships
    abstraction_relation = models.OneToOneField(
        to="epilepsy12.IntegratedCareBoard",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("IntegratedCareBoard KPI Aggregation Model")
        verbose_name_plural = _("IntegratedCareBoard KPI Aggregation Models")

    def get_abstraction_level(self) -> str:
        return EnumAbstractionLevel.ICB

    def get_name(self) -> str:
        return f"{self.abstraction_name}"

    def __str__(self):
        return f"ICBKPIAggregation (IntegratedCareBoard={self.abstraction_relation})"

    def save(self, *args, **kwargs) -> None:
        # UPDATE THE abstraction_name field
        if self.abstraction_relation is not None:
            self.abstraction_name = self.abstraction_relation.ICB_Name
        else:
            self.abstraction_name = "Name not found"
        return super().save(*args, **kwargs)


class NHSRegionKPIAggregation(BaseKPIAggregation):
    """
    KPI summary statistics for NHSRegion.
    """

    # Define relationships
    abstraction_relation = models.OneToOneField(
        to="epilepsy12.NHSEnglandRegion",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("NHSEnglandRegion KPI Aggregation Model")
        verbose_name_plural = _("NHSEnglandRegion KPI Aggregation Models")

    def get_abstraction_level(self) -> str:
        return EnumAbstractionLevel.NHS_REGION

    def get_name(self) -> str:
        return f"{self.abstraction_name}"

    def __str__(self):
        return f"KPIAggregations (NHSEnglandRegion={self.abstraction_relation})"

    def save(self, *args, **kwargs) -> None:
        # UPDATE THE abstraction_name field
        if self.abstraction_relation is not None:
            self.abstraction_name = self.abstraction_relation.NHS_Region
        else:
            self.abstraction_name = "Name not found"
        return super().save(*args, **kwargs)


class OpenUKKPIAggregation(BaseKPIAggregation):
    """
    KPI summary statistics for OpenUK.
    """

    # Define relationships
    abstraction_relation = models.OneToOneField(
        to="epilepsy12.OPENUKNetwork",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("OpenUK KPI Aggregation Model")
        verbose_name_plural = _("OpenUK KPI Aggregation Models")

    def get_abstraction_level(self) -> str:
        return EnumAbstractionLevel.OPEN_UK

    def get_name(self) -> str:
        return f"{self.abstraction_name}"

    def __str__(self):
        return f"OPENUKKPIAggregations (OPENUKNetwork={self.abstraction_relation})"

    def save(self, *args, **kwargs) -> None:
        # UPDATE THE abstraction_name field
        if self.abstraction_relation is not None:
            self.abstraction_name = self.abstraction_relation.OPEN_UK_Network_Name
        else:
            self.abstraction_name = "Name not found"
        return super().save(*args, **kwargs)


class CountryKPIAggregation(BaseKPIAggregation):
    """
    KPI summary statistics for countries.
    """

    # Define relationships
    abstraction_relation = models.OneToOneField(
        to="epilepsy12.Country",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Country KPI Aggregation Model")
        verbose_name_plural = _("Country KPI Aggregation Models")

    def get_abstraction_level(self) -> str:
        return EnumAbstractionLevel.COUNTRY

    def get_name(self) -> str:
        return f"{self.abstraction_name}"

    def __str__(self):
        return f"CountryKPIAggregations (ONSCountryEntity={self.abstraction_relation})"

    def save(self, *args, **kwargs) -> None:
        # UPDATE THE abstraction_name field
        if self.abstraction_relation is not None:
            self.abstraction_name = self.abstraction_relation.Country_ONS_Name
        else:
            self.abstraction_name = "Name not found"
        return super().save(*args, **kwargs)


class NationalKPIAggregation(BaseKPIAggregation):
    """
    KPI summary statistics for England and Wales.
    """

    # National can only have cohort as unique
    cohort = models.PositiveSmallIntegerField(
        unique=True,
    )

    class Meta:
        verbose_name = _("National KPI Aggregation Model")
        verbose_name_plural = _("National KPI Aggregation Models")

    def get_abstraction_level(self) -> str:
        return EnumAbstractionLevel.NATIONAL

    def get_name(self) -> str:
        return "England and Wales"

    def __str__(self):
        return f"National KPIAggregations for England and Wales (Cohort {self.cohort})"
