---
title: Writing Tests
reviewers: Dr Anchit Chandran
---

## Test Structure

Test files are stored in appropriate directories, mirroring the E12 App. Please see [Test Structure](test-structure.md) for details.

The basic structure for test files is as follows:

```python
"""
DOCSTRING GIVING AN OVERVIEW OF THE CONTAINED TESTS
"""

# Standard imports
import pytest

# Third party imports

# RCPCH imports


def test_function_1():
    """
    DOCSTRING DESCRIBING TEST SPECIFICS
    """

    # Test Arrange steps
    ...

    # Test Act steps
    ...

    # Test Assert steps
    assert True == False, "REASON FOR FAILURE"
```

## Real Example

Using a real example:

```python title="epilepsy12/tests/model_tests/test_case.py"
"""
Tests the Case model
"""

# Standard imports
import pytest
from datetime import date

# Third party imports

# RCPCH imports

@pytest.mark.django_db
def test_case_age_calculation(e12_case_factory): # (4)
    # Test that the age function works as expected # (3)
    
    e12Case = e12_case_factory() # (1)
    
    fixed_testing_date = date(2023, 6, 17)
    e12Case.date_of_birth = date(2018, 5, 11)

    assert e12Case.age(fixed_testing_date) == "5 years, 1 month", "Incorrect stringified age" # (2)
```

1.  Arrange & Act Steps: Create necessary Case dependency for test, alongside setting date values to test.
2. Assert Step: asserts the stringified age is correct, with assertion error message.
3. Specific explanation of test.
4. ⚠️ Test names MUST start with `test_` for them to be detected by Pytest.
