---
title: Testing
reviewers: Dr Anchit Chandran
---

There are multiple reasons we may wish to patch values in our tests, including:

- Simulating external service responses
- Controlling return values
- Error handling
- Speeding up tests

For example, [`test_registration_days_remaining_before_submission`](https://github.com/rcpch/rcpch-audit-engine/blob/2393ce8f24724f9ef4f9f6a68bc7074c262e7b7c/epilepsy12/tests/model_tests/test_registration.py#LL184C5-L184C55) relies on calculating the difference in days between `#!python datetime.now().date()` and `#!python Registration.audit_submission_date`.

Of course, `#!python datetime.now().date()` will always change, leading to the tests breaking at some eventual future time point.

Instead, we can temporarily *patch* the return value of `#!python datetime.now().date()`, **only within the scope of this test**, with the `#!python @patch.object()` decorator, using the following syntax:

```python
from unittest.mock import patch

@patch.object(CLASS_NAME_TO_PATCH, 'CLASS_METHOD_NAME_TO_PATCH', return_value=VALUE_TO_RETURN)
```

In action, this looks like this:

```python title="test_registration.py"
from unittest.mock import patch

...

@patch.object(Registration, 'get_current_date', return_value=date(2022, 11, 30))
@pytest.mark.django_db
def test_registration_days_remaining_before_submission(
    mocked_get_current_date,
    example_fresh_registration,
):

    ...
```

We assign the return value of `Registration.get_current_date` to *always* be 2022-11-30.

Using the `#!python @patch.object` decorator also passes in the patched object into the test function as the FIRST parameter, which can be called anything - in this case, we call it `mocked_get_current_date`. Other fixtures required for the test are passed after.

If you use multiple `#!python @patch.object` decorators, patched objects are passed in the same order decorators are evaluated:

```python title="test_registration.py"
from unittest.mock import patch

@patch.object(OBJECT1, 'method_to_patch', return_value=1)
@patch.object(OBJECT2, 'method_to_patch', return_value=3)
@patch.object(OBJECT3, 'method_to_patch', return_value=3)
def test_my_test(
    patched_object_3,
    patched_object_2,
    patched_object_1,
):
    ...
```
