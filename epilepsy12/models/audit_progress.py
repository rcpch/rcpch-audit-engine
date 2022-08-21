from dateutil.relativedelta import relativedelta
from django.db import models


class AuditProgress(models.Model):
    """
    A record is created in the AuditProgress class every time a case is registered for the audit
    It tracks how many fields are complete
    """

    registration_complete = models.BooleanField(
        default=False,
        null=True
    )
    registration_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected",
        default=0,
        null=True
    )
    registration_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed",
        default=0,
        null=True
    )
    initial_assessment_complete = models.BooleanField(
        default=False,
        null=True
    )
    initial_assessment_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected",
        default=0,
        null=True
    )
    initial_assessment_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed",
        default=0,
        null=True
    )
    assessment_complete = models.BooleanField(
        null=True,
        default=False
    )
    assessment_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected",
        default=0,
        null=True
    )
    assessment_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed",
        default=0,
        null=True
    )
    epilepsy_context_complete = models.BooleanField(
        null=True,
        default=False
    )
    epilepsy_context_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected",
        default=0,
        null=True
    )
    epilepsy_context_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed",
        default=0,
        null=True
    )
    multiaxial_description_complete = models.BooleanField(
        null=True,
        default=False
    )
    multiaxial_description_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected",
        default=0,
        null=True
    )
    multiaxial_description_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed",
        default=0,
        null=True
    )
    investigation_complete = models.BooleanField(
        default=False,
        null=True
    )
    investigation_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected",
        default=0,
        null=True
    )
    investigation_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed",
        default=0,
        null=True
    )
    management_complete = models.BooleanField(
        default=False,
        null=True
    )
    management_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected",
        default=0,
        null=True
    )
    management_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed",
        default=0,
        null=True
    )

    class Meta:
        verbose_name = 'Audit Progress'
        verbose_name_plural = 'Audit Progresses'
