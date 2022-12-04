from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from django.db import models
from epilepsy12.models.audit_progress import AuditProgress
from epilepsy12.models.help_text_mixin import HelpTextMixin

from .case import Case
from ..constants import CAN_APPROVE_ELIGIBILITY, CAN_REMOVE_APPROVAL_OF_ELIGIBILITY, CAN_REGISTER_CHILD_IN_EPILEPSY12, CAN_UNREGISTER_CHILD_IN_EPILEPSY12, CAN_ONLY_VIEW_GENERAL_PAEDIATRIC_CENTRE, CAN_ALLOCATE_GENERAL_PAEDIATRIC_CENTRE, CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE, CAN_DELETE_GENERAL_PAEDIATRIC_CENTRE
from ..general_functions import *
from .time_and_user_abstract_base_classes import *
from ..general_functions import first_tuesday_in_january


class Registration(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):
    """
    A record is created in the Registration class every time a case is registered for the audit
    """

    registration_date = models.DateField(
        help_text={
            'label': "First paediatric assessment",
            'reference': "Setting this date is an irreversible step. Confirmation will be requested to complete this step.",
        },
        null=True,
        default=None
    )

    registration_close_date = models.DateField(
        help_text={
            'label': "First paediatric assessment closing date",
            'reference': "Date on which the registration is due to close",
        },
        default=None,
        null=True
    )

    audit_submission_date = models.DateField(
        help_text={
            'label': "Epilepsy12 submission date",
            'reference': "Date on which the audit submission is due. It is always on the 2nd Tuesday in January.",
        },
        default=None,
        null=True
    )

    def audit_submission_date_calculation(self):
        if (self.registration_date):
            this_year = date.today().year
            second_tuesday_this_year = first_tuesday_in_january(
                this_year) + relativedelta(days=7)
            if date.today() <= second_tuesday_this_year:
                second_tuesday = second_tuesday_this_year
            else:
                second_tuesday = first_tuesday_in_january(
                    this_year+1) + relativedelta(days=7)
            return second_tuesday
        else:
            return None

    def registration_date_one_year_on(self):
        if (self.registration_date):
            return self.registration_date+relativedelta(years=1)
        else:
            return None

    eligibility_criteria_met = models.BooleanField(
        default=None,
        null=True
    )

    cohort = models.PositiveSmallIntegerField(
        default=None,
        null=True
    )

    @property
    def days_remaining_before_submission(self):
        if self.audit_submission_date:
            today = datetime.now().date()
            # remaining_time = relativedelta(
            #     self.audit_submission_date, today)
            remaining_time = self.audit_submission_date - today
            if remaining_time.days < 0:
                return 0
            return remaining_time.days

    # relationships
    case = models.OneToOneField(
        Case,
        on_delete=models.PROTECT,
        null=True
    )

    audit_progress = models.OneToOneField(
        AuditProgress,
        on_delete=models.CASCADE,
        null=True
    )

    class Meta:
        verbose_name = 'Registration'
        verbose_name_plural = 'Registrations'
        permissions = [
            CAN_APPROVE_ELIGIBILITY,
            CAN_REMOVE_APPROVAL_OF_ELIGIBILITY,
            CAN_REGISTER_CHILD_IN_EPILEPSY12,
            CAN_UNREGISTER_CHILD_IN_EPILEPSY12,
            CAN_ONLY_VIEW_GENERAL_PAEDIATRIC_CENTRE,
            CAN_ALLOCATE_GENERAL_PAEDIATRIC_CENTRE,
            CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE,
            CAN_DELETE_GENERAL_PAEDIATRIC_CENTRE,
        ]

    def save(self, *args, **kwargs) -> None:
        if self.registration_date is not None:
            self.registration_close_date = self.registration_date_one_year_on()
            self.audit_submission_date = self.audit_submission_date_calculation()
            self.cohort = cohort_number_from_enrolment_date(
                self.registration_date)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.registration_date:
            return f'Epilepsy12 registration for {self.case} on {self.registration_date}'
        else:
            return f'Epilepsy12 registration for {self.case} incomplete.'
