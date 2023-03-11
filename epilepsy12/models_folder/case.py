# python
from dateutil import relativedelta
from datetime import date
import math

# django
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField, DateField
from django.conf import settings

# 3rd party
from simple_history.models import HistoricalRecords

# epilepsy12
from .help_text_mixin import HelpTextMixin
from ..constants import SEX_TYPE, ETHNICITIES, UNKNOWN_POSTCODES, CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING, CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING, CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT, CAN_CONSENT_TO_AUDIT_PARTICIPATION
from ..general_functions import imd_for_postcode
from .time_and_user_abstract_base_classes import *


class Case(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):
    """
    This class holds information about each child or young person
    Each case is unique
    """
    # _id = models.ObjectIdField()
    locked = models.BooleanField(
        """
        This determines if the case is locked from editing
        Cases can be locked under either of 2 sets of circumstances
        1. The child has opted out of the audit 
        - here all data relating to the child's ID is set to None but the ID retained.
        - in the UI, blank spaces in the case_list are rendered as ######
        2. All the fields for the child have been completed and the user has indicated the child is ready for submission.
        - The upload button in the UI is enabled up until the submission deadline to toggle the locked status
        3. The submission deadline has passed. The case is locked, irrespective of if fields are complete are not.
        """
        "Locked",
        default=False,
        blank=True,
        null=True
    )
    locked_at = models.DateTimeField(
        "Date record locked",
        null=True,
        blank=True
    )
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        verbose_name="locked by",
        null=True,
        blank=True
    )
    # nhs_patient = models.BooleanField(
    #     "Is an NHS patient?"
    # )
    nhs_number = models.CharField(  # the NHS number for England and Wales - THIS IS NOT IN THE ORIGINAL TABLES
        "NHS Number",
        unique=True,
        blank=True,
        null=True,
        max_length=10
        # validators=[MinLengthValidator(  # should be other validation before saving - need to strip out spaces
        #     limit_value=10,
        #     message="The NHS number must be 10 digits long."
        # )]
    )  # TODO #13 NHS Number must be hidden - use case_uuid as proxy
    first_name = CharField(
        "first name",
        max_length=100,
        blank=True,
        null=True,
    )
    surname = CharField(
        "surname",
        max_length=100,
        blank=True,
        null=True,
    )
    sex = models.IntegerField(
        choices=SEX_TYPE,
        blank=True,
        null=True,
    )
    date_of_birth = DateField(
        "date of birth (YYYY-MM-DD)",
        blank=True,
        null=True,
    )
    postcode = CharField(
        "postcode",
        max_length=8,
        blank=True,
        null=True,
        # validators=[validate_postcode]
    )

    ethnicity = CharField(
        max_length=4,
        choices=ETHNICITIES,
        blank=True,
        null=True
    )

    index_of_multiple_deprivation_quintile = models.PositiveSmallIntegerField(
        # this is a calculated field - it relies on the availability of the Deprivare server running
        # A quintile is calculated on save and persisted in the database
        "index of multiple deprivation calculated from MySociety data.",
        blank=True,
        editable=False,
        null=True
    )

    history = HistoricalRecords()

    # relationships
    hospital_trusts = models.ManyToManyField(
        'epilepsy12.HospitalTrust',
        through='Site',
        related_name='cases',
        through_fields=('case', 'hospital_trust')
    )

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    @property
    def age(self):
        today = date.today()
        calculated_age = relativedelta.relativedelta(
            today, self.date_of_birth)
        months = calculated_age.months
        years = calculated_age.years
        weeks = calculated_age.weeks
        days = calculated_age.days
        final = ''
        if years == 1:
            final += f'{calculated_age.years} year'
            if (months/12) - years == 1:
                final += f'{months} month'
            elif (months/12)-years > 1:
                final += f'{math.floor((months*12)-years)} months'
            else:
                return final

        elif years > 1:
            final += f'{calculated_age.years} years'
            if (months/12) - years == 1:
                final += f', {months} month'
            elif (months/12)-years > 1:
                final += f', {math.floor((months*12)-years)} months'
            else:
                return final
        else:
            # under a year of age
            if months == 1:
                final += f'{months} month'
            elif months > 0:
                final += f'{months} months, '
                if weeks >= (months*4):
                    if (weeks-(months*4)) == 1:
                        final += '1 week'
                    else:
                        final += f'{math.floor(weeks-(months*4))} weeks'
            else:
                if weeks > 0:
                    if weeks == 1:
                        final += f'{math.floor(weeks)} week'
                    else:
                        final += f'{math.floor(weeks)} weeks'
                else:
                    if days > 0:
                        if days == 1:
                            final += f'{math.floor(days)} day'
                        if days > 1:
                            final += f'{math.floor(days)} days'
                    else:
                        final += 'Happy birthday'
        return final

    def save(
            self,
            *args, **kwargs) -> None:

        # This field requires the deprivare api to be running
        # note if one of ['ZZ99 3CZ','ZZ99 3GZ','ZZ99 3WZ','ZZ99 3VZ'], represent not known, not known - England,
        # not known - Wales or no fixed abode
        if self.postcode and self.postcode not in UNKNOWN_POSTCODES:
            self.index_of_multiple_deprivation_quintile = imd_for_postcode(
                self.postcode)
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Deleting a Case involves deleting any registrations associated that exist first
        try:
            self.registration.delete()
        except:
            pass
        super(Case, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        # custom permissions for Case class
        permissions = [
            CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING,
            CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING,
            CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT,
            CAN_CONSENT_TO_AUDIT_PARTICIPATION
        ]

    def __str__(self) -> str:
        return f'{self.first_name} {self.surname}'
