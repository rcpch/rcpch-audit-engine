# python
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# django
from django.contrib.gis.db import models

# 3rd party
from simple_history.models import HistoricalRecords

# rcpch
from .help_text_mixin import HelpTextMixin
from ..constants import (
    CAN_APPROVE_ELIGIBILITY,
    CAN_REGISTER_CHILD_IN_EPILEPSY12,
    CAN_UNREGISTER_CHILD_IN_EPILEPSY12,
    CAN_CONSENT_TO_AUDIT_PARTICIPATION,
)
from .time_and_user_abstract_base_classes import *
from ..general_functions import (
    dates_for_cohort,
    cohort_number_from_first_paediatric_assessment_date,
)
from ..validators import not_in_the_future_validator


class Registration(
    TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin
):
    """
    A record is created in the Registration class every time a case is registered for the audit
    """

    first_paediatric_assessment_date = models.DateField(
        help_text={
            "label": "First paediatric assessment",
            "reference": "'First paediatric assessment' is when the patient was initally seen by a paedaitric professional for parozysmal episodes in any healthcare setting. Setting this date is an irreversible step. Confirmation will be requested to complete this step.",
        },
        null=True,
        default=None,
        validators=[not_in_the_future_validator],
    )

    completed_first_year_of_care_date = models.DateField(
        help_text={
            "label": "First year of care completion date",
            "reference": "Date which completes first year of epilepsy care",
        },
        default=None,
        null=True,
    )

    # this should deprecate as can be calculated from cohort
    audit_submission_date = models.DateField(
        help_text={
            "label": "Epilepsy12 submission date",
            "reference": "Date on which the audit submission is due. It is always on the 2nd Tuesday in January.",
        },
        default=None,
        null=True,
    )

    eligibility_criteria_met = models.BooleanField(default=None, null=True)

    cohort = models.PositiveSmallIntegerField(default=None, null=True)

    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    def get_current_date(self):
        return datetime.now().date()

    @property
    def days_remaining_before_submission(self) -> int:
        """Returns remaining days between current datetime and submission datetime, minimum value 0."""
        if self.audit_submission_date:
            remaining_datetime = self.audit_submission_date - self.get_current_date()
            if remaining_datetime.days is None or remaining_datetime.days < 0:
                return 0
            else:
                return remaining_datetime.days

    # relationships
    case = models.OneToOneField("epilepsy12.Case", on_delete=models.PROTECT, null=True)

    audit_progress = models.OneToOneField(
        "epilepsy12.AuditProgress", on_delete=models.CASCADE, null=True
    )

    kpi = models.OneToOneField("epilepsy12.KPI", on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Registration"
        verbose_name_plural = "Registrations"
        ordering = ["case"]
        permissions = [
            CAN_APPROVE_ELIGIBILITY,
            CAN_REGISTER_CHILD_IN_EPILEPSY12,
            CAN_UNREGISTER_CHILD_IN_EPILEPSY12,
            CAN_CONSENT_TO_AUDIT_PARTICIPATION,
        ]

    def save(self, *args, **kwargs) -> None:
        if self.first_paediatric_assessment_date is not None:
            self.cohort = cohort_number_from_first_paediatric_assessment_date(
                self.first_paediatric_assessment_date
            )
            cohort_data = dates_for_cohort(self.cohort)
            self.completed_first_year_of_care_date = (
                self.first_paediatric_assessment_date + relativedelta(years=1)
            )
            self.audit_submission_date = cohort_data["submission_date"]

        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.first_paediatric_assessment_date:
            return f"Epilepsy12 registration for {self.pk} - {self.case} on {self.first_paediatric_assessment_date}"
        else:
            return f"Epilepsy12 registration for {self.case} incomplete."
