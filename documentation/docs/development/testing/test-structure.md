---
reviewers: Dr Anchit Chandran
---

Global Pytest configuration settings are set within `pytest.ini`, in the top-level directory of the Django project.

Tests related to Epilepsy12 are found in the `epilepsy12/tests` directory.

This is an overview of their contents.

## Factories, fixtures, meta tests

| Module        | Description                                                                                                     |
| :------------ | :-------------------------------------------------------------------------------------------------------------- |
| `_meta_tests` | Folder containing tests related to tests concerning the actual test environment setup, such as test-db seeding. |
| `factories`   | Module containing all FactoryBoy factories.                                                                     |
| `conftest.py` | Defines global fixtures.                                                                                        |

## Test directories

We aim for 100% test coverage. To this end, our test directory name-spacing mirrors that of the E12 App.

| Directory                        | Description                                                       |
| :---------------------------- | :---------------------------------------------------------------- |
| `common_view_functions_tests` | Folder containing tests related to the `common_view_functions`.   |
| `general_functions_tests`     | Folder containing tests related to the `general_functions_tests`. |
| `model_tests`                 | Folder containing tests related to the `model_tests`.             |
| `view_tests`                  | Folder containing tests related to the `view_tests`.              |
