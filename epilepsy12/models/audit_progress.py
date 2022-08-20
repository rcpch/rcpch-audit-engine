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
    initial_assessment_complete = models.BooleanField(
        default=False,
        null=True
    )
    assessment_complete = models.BooleanField(
        null=True,
        default=False
    )
    epilepsy_context_complete = models.BooleanField(
        null=True,
        default=False
    )
    multiaxial_description_complete = models.BooleanField(
        null=True,
        default=False
    )
    investigation_management_complete = models.BooleanField(
        default=False,
        null=True
    )

    class Meta:
        verbose_name = 'Audit Progress'
