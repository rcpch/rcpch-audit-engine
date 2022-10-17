from django.db import models
from functools import partial as curry
from ..constants import CHRONICITY, DIAGNOSTIC_STATUS
from .time_and_user_abstract_base_classes import *

# other tables
from .registration import Registration


class InitialAssessment(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class records information about the initial assessment.
    Whilst other information about the child and their epilepsy may be captured across the audit year
    in the assessment table, this information MUST be collected at the first visit.
    This class references the Case class as a case can have multiple episodes.
    This class references the EEG class as an episode can have multiple EEGs

    This whole clase might better belong in the initial assessment

    """

    # date_of_initial_assessment = models.DateField(
    #     "On what date did the initial assessment occur?",
    #     null=True,
    #     default=None
    # )
    # general_paediatrics_referral_made = models.BooleanField(
    #     "date of referral to general paediatrics",
    #     null=True,
    #     default=None
    # )
    # date_of_referral_to_general_paediatrics = models.DateField(
    #     "date of referral to general paediatrics",
    #     null=True,
    #     default=None
    # )
    first_paediatric_assessment_in_acute_or_nonacute_setting = models.IntegerField(
        help_text={
            'label': "Is the first paediatric assessment in an acute or nonacute setting?",
            'reference': "Is the first paediatric assessment in an acute or nonacute setting?"
        },
        choices=CHRONICITY,
        null=True,
        default=None
    )
    # has_description_of_the_episode_or_episodes_been_gathered = models.BooleanField(
    #     help_text={
    #         'label': ,
    #         'reference': "has a description of the episode(s) been gathered?"
    #     },
    #     null=True,
    #     default=None
    # )
    has_number_of_episodes_since_the_first_been_documented = models.BooleanField(
        help_text={
            'label': 'The approximate frequency or number of episodes since the first episode',
            'reference': "Has the approximate frequency or number of episodes since the first recorded episode been documented?"
        },
        null=True,
        default=None
    )
    general_examination_performed = models.BooleanField(
        help_text={
            'label': 'General examination',
            'reference': "has a general paediatric examination been performed?"
        },
        null=True,
        default=None
    )
    neurological_examination_performed = models.BooleanField(
        help_text={
            'label': 'Neurological examination',
            'reference': "Has a neurological examination been performed?"
        },
        null=True,
        default=None
    )
    developmental_learning_or_schooling_problems = models.BooleanField(
        help_text={
            'label': 'Presence or absence of learning, developmental or educational difficulties',
            'reference': "Has the presence or absence of developmental, learning or school-based problems been recorded?",
        },
        null=True,
        default=None
    )
    behavioural_or_emotional_problems = models.BooleanField(
        help_text={
            'label': 'Presence or absence of emotional or behavioural problems',
            'reference': "Has the presence or absence of emotional or behavioural problems been documented?",
        },
        null=True,
        default=None
    )

    # diagnostic_status = models.CharField(  # This currently essential - used to exclude nonepilepic kids
    #     max_length=1,
    #     choices=DIAGNOSTIC_STATUS,
    #     verbose_name="Status of epilepsy diagnosis. Must have epilepsy or probable epilepsy to be included.",
    #     default=None,
    #     null=True
    # )

    # relationships
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        verbose_name="Related Registration"
    )

    class Meta:
        # indexes = [models.Index(fields=['date_of_initial_assessment'])]
        verbose_name = 'First Paediatric Assessment'
        verbose_name_plural = 'First Paediatric Assessments'

    def _get_help_label_text(self, field_name):
        """Given a field name, return it's label help text."""
        for field in self._meta.fields:
            if field.name == field_name:
                return field.help_text['label']

    def _get_help_reference_text(self, field_name):
        """Given a field name, return it's reference help text."""
        for field in self._meta.fields:
            if field.name == field_name:
                return field.help_text['reference']

    def save(
            self,
            *args, **kwargs) -> None:
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.date_of_initial_assessment:
            return f"First Paediatric Assessment for {self.registration.case} on {self.date_of_initial_assessment}"
        else:
            return f"{self.registration.case} has not yet had First Paediatric Assessment."

    def __init__(self, *args, **kwargs) -> None:
        super(InitialAssessment, self).__init__(*args, **kwargs)
        """
        Thanks https://bradmontgomery.net/blog/django-hack-help-text-modal-instance/ for this snippet
        Returns the help text methods to the template
        Can use {{initial_assessment.get_*field*_help_label_text}} and {{initial_assessment.get_*field*_help_reference_text}}
        in the template
        """

        # Again, iterate over all of our field objects.
        for field in self._meta.fields:
            # Create a string, get_FIELDNAME_help text
            label_method_name = "get_{0}_help_label_text".format(field.name)
            reference_method_name = "get_{0}_help_reference_text".format(
                field.name)

            # We can use curry to create the method with a pre-defined argument
            label_curried_method = curry(
                self._get_help_label_text, field_name=field.name)
            reference_curried_method = curry(
                self._get_help_reference_text, field_name=field.name)

            # And we add this method to the instance of the class.
            setattr(self, label_method_name, label_curried_method)
            setattr(self, reference_method_name, reference_curried_method)
