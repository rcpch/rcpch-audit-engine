---
reviewers: Dr Anchit Chandran
---

Pytest and FactoryBoy factories and fixtures enable DRY code, allowing similar object instances to be defined once, and shared many times across the test directory, enabling faster and more consistent test-driven development.

For example, many of the tests rely on the creation of a fully-completed audit, which is comprised of the following:

1. `Case` model with linked `Organisation`(s), through the `Site` conduit model

   1. Linked `Registration` model

      1. Linked `AuditProgress` model
      1. Linked `KPI` model
      1. Linked `FirstPaediatricAssessment` model
      1. Linked `EpilepsyContext` model
      1. Linked `MultiaxialDiagnosis` model
      1. Linked `Assessment` model
      1. Linked `Investigations` model
      1. Linked `Management` model

Following the best-practice principle of DRY code, we use FactoryBoy factories to define the creation of Epilepsy12 `Case` instances, with default values set once, minimising repeated code. Whenever an object is created using the 'top-level' `e12_case_factory`, all the linked dependency models have generated automatically, with default values that can be overridden.

## `conftest.py`

The `conftest.py` file registers fixtures globally to be used in any test without import. Available factories are imported and registered like so:

```python
from epilepsy12.tests.factories import (
    E12CaseFactory,
    ... # other factories
)

register(E12CaseFactory)  # => e12_case_factory
```

When factories are registered this way, their default fixture name becomes the lowercase, under-score version of the class name. In this case, `E12CaseFactory`'s fixture becomes `e12_case_factory`, which can be used like so:

```python
@pytest.mark.django_db
def test_example(e12_case_factory):

    fully_completed_case = e12_case_factory()
```

--8<--
docs/_assets/_snippets/pytest-db-access.md
--8<--

## Using E12Factories

As factories have been registered within `conftest.py`, whenever a factory is required in a test, pass in the lowercase, under-scored fixture name into the test arguments:

```python
@pytest.mark.django_db
def test_example(
    e12_case_factory
):
    ...
```

Each E12 model has an associate factory, whose fixtures are namespaced using the `e12_LOWERCASE_UNDERSCORE_MODELNAME_factory` e.g. pattern:

```python
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
```

### Usage

For most test cases, which require multiple different linked models (e.g. a `Registration` attached to a `MultiaxialDiagnosis`), you should instantiate starting from the `e12_case_factory`:

```python
@pytest.mark.django_db
def test_example(
    e12_case_factory
):
    case = e12_case_factory()
```


This will create and save a fully-registered and audit-complete `Case`, accessible using the `case` variable.

### Accessing values and overriding defaults

Default attributes of the `Case` model can be overridden:

```python
@pytest.mark.django_db
def test_example(
    e12_case_factory
):
    case = e12_case_factory(
        first_name = "Bob",
        surname = "Dylan",
    )
```

Dependency factory attributes can be directly overridden, up to 2 dependencies down (the factories directly related to a `Registration`), using the dunder-format:

```python
@pytest.mark.django_db
def test_example(
    e12_case_factory
):
    case = e12_case_factory(

        # Case.first_name
        first_name = "Bob",

        # Case.surname
        surname = "Dylan",

        # Registration.registration_date
        registration__registration_date=date(2023,1,1),

        # Assessment.childrens_epilepsy_surgical_service_referral_criteria_met WHERE Assessment.registration is linked to this instance
        registration__assessment__childrens_epilepsy_surgical_service_referral_criteria_met=True,

        # Investigations.mri_brain_requested_date WHERE Investigations.registration is linked to this instance
        registration__investigations__mri_brain_requested_date=date(2023,4,1)
    )
```

Values can be directly accessed up to 2 dependencies down:

```python
print(case.first_name) # => Bob
print(case.registration) # => Epilepsy12 registration for Bob Dylan on 2023-01-01
print(case.registration.multiaxialdiagnosis) # => Multaxial diagnosis for Bob Dylan
print(case.registration.multiaxialdiagnosis.syndrome_present) # => True
```

!!!info "Accessing `Multiaxial_Diagnosis` attribute"
    NOTE: to access `Multiaxial_Diagnosis` in this way, use the lowercased, non-underscored name: `multiaxialdiagnosis`

These all return Django model objects, which can be used in the classic Django way if further customisation is required for tests:

```python title="epilepsy12/tests/common_view_functions_tests/calculate_kpi_tests/test_measure_5.py"
from epilepsy12.models import (
    Registration,
    Syndrome,
)

@pytest.mark.django_db
def test_measure_4_mri_syndromes_ineligible(
    e12_case_factory,
    ...
):

    ...

    case = e12_case_factory()

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    # get syndrome for registration
    current_syndromes = Syndrome.objects.get(
        multiaxial_diagnosis=registration.multiaxialdiagnosis
    )

    ...

```

### Flags

Specific factories contain flags that override multiple values if set `True`. For example, the `E12_Assessment_Factory` assigns `consultant_paediatrician_referral_made=True` by default, with `consultant_paediatrician_referral_date` and `consultant_paediatrician_input_date`.

The `Assessment.no_referral_consultant_paediatrician=True` flag can be used to override this:

```python
@pytest.mark.django_db
def test_testing(
    e12_case_factory
):
    
    case = e12_case_factory(
        registration__assessment__no_referral_consultant_paediatrician=True
    )
    
    print(case.registration.assessment.consultant_paediatrician_referral_made) # => False
    print(case.registration.assessment.consultant_paediatrician_referral_date) # => None
    print(case.registration.assessment.consultant_paediatrician_input_date) # => None
```
