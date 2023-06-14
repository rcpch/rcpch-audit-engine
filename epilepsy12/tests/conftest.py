"""conftest.py
Configures pytest fixtures for epilepsy12 app tests.
"""

# standard imports
from datetime import date

# third-party imports
import pytest
from pytest_factoryboy import register

# rcpch imports
from epilepsy12.tests.factories import (
    seed_groups_fixture,
    cases_seeder,
    E12AntiEpilepsyMedicineFactory,
    E12AssessmentFactory,
    E12CaseFactory,
    E12ComorbidityFactory,
    E12EpilepsyContextFactory,
    E12EpisodeFactory,
    E12FirstPaediatricAssessmentFactory,
    E12ManagementFactory,
    E12MultiaxialDiagnosisFactory,
    E12RegistrationFactory,
    E12SiteFactory,
    E12SyndromeFactory,
    E12UserFactory,
)


# register factories to be used across test directory

# factory object becomes lowercase-underscore form of the class name
register(E12AntiEpilepsyMedicineFactory)  # => e12_anti_epilepsy_medicine_factory
register(E12AssessmentFactory)  # => e12_assessment_factory
register(E12CaseFactory)  # => e12_case_factory
register(E12ComorbidityFactory)  # => e12_comborbidity_factory
register(E12EpilepsyContextFactory)  # => e12_epilepsy_context
register(E12EpisodeFactory)  # => e12_episode_factory
register(E12FirstPaediatricAssessmentFactory)  # => e12_first_paediatric_assessment_factory
register(E12ManagementFactory)  # => e12_management_factory
register(E12MultiaxialDiagnosisFactory)  # => e12_multiaxial_diagnosis_factory
register(E12RegistrationFactory)  # => e12_registration_factory
register(E12SiteFactory)  # => e12_site_factory
register(E12SyndromeFactory) # => e12_syndrome_factory
register(E12UserFactory)  # => e12_user_factory
