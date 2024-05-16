from django.apps import apps
from django.contrib.gis.db import models
from .help_text_mixin import HelpTextMixin


class AuditProgress(models.Model, HelpTextMixin):
    """
    A record is created in the AuditProgress class every time a case is registered for the audit
    It tracks how many fields are complete
    """

    registration_complete = models.BooleanField(default=False, null=True)
    registration_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected", default=0, null=True
    )
    registration_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed", default=0, null=True
    )
    first_paediatric_assessment_complete = models.BooleanField(default=False, null=True)
    first_paediatric_assessment_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected", default=0, null=True
    )
    first_paediatric_assessment_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed", default=0, null=True
    )
    assessment_complete = models.BooleanField(null=True, default=False)
    assessment_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected", default=0, null=True
    )
    assessment_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed", default=0, null=True
    )
    epilepsy_context_complete = models.BooleanField(null=True, default=False)
    epilepsy_context_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected", default=0, null=True
    )
    epilepsy_context_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed", default=0, null=True
    )
    multiaxial_diagnosis_complete = models.BooleanField(null=True, default=False)
    multiaxial_diagnosis_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected", default=0, null=True
    )
    multiaxial_diagnosis_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed", default=0, null=True
    )
    investigations_complete = models.BooleanField(default=False, null=True)
    investigations_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected", default=0, null=True
    )
    investigations_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed", default=0, null=True
    )
    management_complete = models.BooleanField(default=False, null=True)
    management_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected", default=0, null=True
    )
    management_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed", default=0, null=True
    )

    consent_patient_confirmed = models.BooleanField(default=None, null=True)

    details_patient_confirmed = models.BooleanField(default=None, null=True)

    """
    Calculated fields
    """

    @property
    def total_completed_fields(self):
        total_fields = 0
        if self.registration_total_completed_fields:
            total_fields += self.registration_total_completed_fields
        if self.first_paediatric_assessment_total_completed_fields:
            total_fields += self.first_paediatric_assessment_total_completed_fields
        if self.assessment_total_completed_fields:
            total_fields += self.assessment_total_completed_fields
        if self.epilepsy_context_total_completed_fields:
            total_fields += self.epilepsy_context_total_completed_fields
        if self.multiaxial_diagnosis_total_completed_fields:
            total_fields += self.multiaxial_diagnosis_total_completed_fields
        if self.investigations_total_completed_fields:
            total_fields += self.investigations_total_completed_fields
        if self.management_total_completed_fields:
            total_fields += self.management_total_completed_fields
        return total_fields

    @property
    def total_expected_fields(self):
        total_fields = 0
        if self.registration_total_expected_fields:
            total_fields += self.registration_total_expected_fields
        else:
            total_fields += 3
        if self.first_paediatric_assessment_total_expected_fields:
            total_fields += self.first_paediatric_assessment_total_expected_fields
        else:
            total_fields += 6
        if self.assessment_total_expected_fields:
            total_fields += self.assessment_total_expected_fields
        else:
            total_fields += 5
        if self.epilepsy_context_total_expected_fields:
            total_fields += self.epilepsy_context_total_expected_fields
        else:
            total_fields += 8
        if self.multiaxial_diagnosis_total_expected_fields:
            total_fields += self.multiaxial_diagnosis_total_expected_fields
        else:
            total_fields += 10
        if self.investigations_total_expected_fields:
            total_fields += self.investigations_total_expected_fields
        else:
            total_fields += 4
        if self.management_total_expected_fields:
            total_fields += self.management_total_expected_fields
        else:
            total_fields += 5

        return total_fields

    @property
    def audit_complete(self):
        if (
            self.registration_complete
            and self.first_paediatric_assessment_complete
            and self.epilepsy_context_complete
            and self.assessment_complete
            and self.multiaxial_diagnosis_complete
            and self.investigations_complete
            and self.management_complete
        ):
            return True
        else:
            return False

    def __str__(self):
        Registration = apps.get_model("epilepsy12", "Registration")
        Site = apps.get_model("epilepsy12", "Site")
        registration = Registration.objects.filter(audit_progress=self).first()
        if registration:
            lead_site = Site.objects.get(
                case=registration.case,
                site_is_actively_involved_in_epilepsy_care=True,
                site_is_primary_centre_of_epilepsy_care=True,
            )
            return f"Audit progress for {self.registration.case} [{lead_site.organisation}](cohort {registration.cohort})"
        else:
            return f"No AuditProgress record yet"

    class Meta:
        verbose_name = "Audit Progress"
        verbose_name_plural = "Audit Progresses"
        ordering = ["registration__case"]
