from dateutil import relativedelta
import math
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField, DateField
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

from ..constants import *
from ..general_functions import *
from .time_and_user_abstract_base_classes import *


class Case(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class holds information about each child or young person
    Each case is unique
    This class holds patient characteristics including identifiers
    This class is referenced by the Site class, as each case can be seen in multiple sites
    This class is referenced by the Neurodevelopmental class as each case can have multiple neurodevelopmental conditions
    This class is referenced by the MentalHealth class as each case can have multiple mental health conditions
    This class is referenced by the EpilepsyContext class as each case may optionally have contextual information that may inform the epilepsy history

    For a record to be locked:
    1. all mandatory fields must be complete
    2. NHS number must be present
    3. 1 year must have passed

    ?analysis flag
    """
    locked = models.BooleanField(  # this determines if the case is locked from editing ? are cases or only registrations locked?
        "Locked",
        default=False
    )
    locked_at = models.DateTimeField(
        "Date record locked",
        auto_now_add=True
    )
    locked_by = models.ForeignKey(
        User,
        on_delete=CASCADE,
        verbose_name="locked by",
        default=None
    )
    nhs_patient = models.BooleanField(
        "Is an NHS patient?"
    )
    nhs_number = models.CharField(  # the NHS number for England and Wales - THIS IS NOT IN THE ORIGINAL TABLES
        "NHS Number",
        max_length=10
        # validators=[MinLengthValidator(  # should be other validation before saving - need to strip out spaces
        #     limit_value=10,
        #     message="The NHS number must be 10 digits long."
        # )]
    )  # TODO #13 NHS Number must be hidden - use case_uuid as proxy
    first_name = CharField(
        "first name",
        max_length=100
    )
    surname = CharField(
        "surname",
        max_length=100
    )
    gender = models.IntegerField(
        choices=SEX_TYPE
    )
    date_of_birth = DateField(
        "date of birth (YYYY-MM-DD)"
    )
    postcode = CharField(
        "postcode",
        max_length=7,
        # validators=[validate_postcode]
    )

    ethnicity = CharField(
        max_length=4,
        choices=ETHNICITIES
    )

    @property
    def age(self):
        today = date.today()
        calculated_age = relativedelta.relativedelta(
            today, self.date_of_birth)
        months = calculated_age.months
        years = calculated_age.years
        weeks = calculated_age.weeks
        days = calculated_age.days
        print(years, months, weeks, days, date.today(), self.date_of_birth)
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

    # This field requires the deprivare api to be running
    def _imd_quintile_from_postcode(self) -> int:
        "index of multiple deprivation calculated from MySociety data.",
        if (self.postcode):
            postcode = valid_postcode(self.postcode)
            imd_quintile = imd_for_postcode(postcode)
            return imd_quintile

    class Meta:
        # indexes = [models.Index(fields=['case_uuid'])]
        verbose_name = 'case'
        verbose_name_plural = 'cases'

    def __str__(self) -> str:
        return self.first_name + " " + self.surname
