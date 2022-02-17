from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField, DateField
from django.contrib.auth.models import User
import uuid
from ..constants import *
from .time_and_user_mixin import TimeAndUserStampMixin

# other tables
from .assessment import Assessment

class Case(TimeAndUserStampMixin):
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
    case_uuid=models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    locked=models.BooleanField( # this determines if the case is locked from editing ? are cases or only registrations locked?
        "Locked", 
        default=False
    )
    locked_at = models.DateTimeField(
        auto_now_add=True
    )
    locked_by = models.ForeignKey(
        User, 
        on_delete=CASCADE,
        related_name='case_locked'
    )
    nhs_patient = models.CharField(
        max_length=2, 
        choices=OPT_OUT
    )
    nhs_number = models.IntegerField( # the NHS number for England and Wales - THIS IS NOT IN THE ORIGINAL TABLES
        max_length=10,
        validators=[MinLengthValidator( # should be other validation before saving - need to strip out spaces
            limit_value=10,
            message="The NHS number must be 10 digits long."
        )]
    ) # TODO #13 NHS Number must be hidden - use case_uuid as proxy
    first_name=CharField(
        max_length=100
    )
    surname=CharField(
        max_length=100
    )
    gender=CharField(
        max_length=2,
        choices=SEX_TYPE
    )
    date_of_birth=DateField()
    postcode=CharField( # TODO #6 need to validate postcode
        max_length=7
    )
    index_of_multiple_deprivation=CharField( # TODO #5 need to calculate IMD and persist
        
    )
    index_of_multiple_deprivation_quintile=CharField( # TODO #4 need to calculate IMD quintile and persist

    )
    
    ethnicity=CharField(
        # TODO #7 There needs to be a standard look up for ethnicities - DM&D
        max_length=4,
        choices=ETHNICITIES
    )

    class Meta: #TODO #16 add meta classes to all classes
        indexes=[models.Index(fields=['case_uuid'])]
        ordering = ['-surname']
        verbose_name = 'child or young person'
        verbose_name_plural = 'children and young people'

    def __str__(self) -> str:
        return self.hospital_trust_name