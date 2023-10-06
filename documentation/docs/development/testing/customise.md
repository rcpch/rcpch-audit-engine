---
reviewers: Dr Anchit Chandran
---

## `pytest.ini`

The `pytest.ini` file in the project root defines configurations for our tests.

Take this example:

```ini
[pytest]

# POINT PYTEST AT PROJECT SETTINGS
DJANGO_SETTINGS_MODULE = rcpch-audit-engine.settings

# SET FILENAME FORMATS OF TESTS
python_files = test_*.py


addopts =
    --reuse-db # RE USE TEST DB AS DEFAULT
    -k "not examples" # AVOID TESTS MARKED AS EXAMPLES

markers =
    examples: mark test as workshop-type / example test
    seed: mark test as 'meta test', just used for seeding
```

| Configuration Option                                                                                     | Description                                                                                                                             |
| :------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| [`addopts`](https://docs.pytest.org/en/7.1.x/reference/reference.html?highlight=addopts#confval-addopts) | Adds arguments to the `pytest` command by default. E.g. running `pytest` actually results in: <br>`pytest --reuse-db -k "not examples"` |
| `markers`                                                                                                | Define additional markers to selectively run tests.                                                                                     |

## Markers

Pytest allows the use of 'mark'ing tests. Custom marks can be added in [`pytest.ini`](#pytestini).

Marks are applied by using the Pytest decorator over test functions, which can be chained e.g.:

```python
@pytest.mark.xfail
@pytest.mark.parametrize(
    "DATE_OF_BIRTH,REGISTRATION_DATE,TIMELY_MRI,EXPECTED_SCORE",
    [
        (date(2022, 1, 1),date(2024, 1, 1),True,KPI_SCORE["PASS"],),
        (date(2022, 1, 1),date(2024, 1, 1),False,KPI_SCORE["FAIL"],),
        (date(2022, 1, 1),date(2024, 1, 2),True,KPI_SCORE["NOT_APPLICABLE"],),
    ],
)
@pytest.mark.django_db
def test_measure_4_mri_under2yo(
    ...
)
```

Default marks are included with Pytest. Some of these include:

| <div style="width:200px">Mark</div> | Description                                                                                                    |
| :---------------------------------- | :------------------------------------------------------------------------------------------------------------- |
| `@pytest.mark.xfail`                | Mark which labels test as expected fail, used for Test-Driven-Development where tests are written before code. |
| `@pytest.mark.django_db`            | Mark which enables test-db access.                                                                             |
| `@pytest.mark.parametrize`          | Mark which parametrizes test functions.                                                                        |

## Selecting tests through name

The `-k` flag will select and run tests based on the provided substring.

For example, the following commands will collect and run tests starting with `test_measure_1`:

=== "Using Docker Desktop"
`console
    pytest -k "test_measure_1"
    `

=== "Using docker compose"
`console
    sudo docker compose -f docker-compose.dev-init.yml exec web pytest -k "test_measure_1"
    `

## Skipping or selecting tests

Some of the more time-consuming tests can be skipped for convenience using the ['mark' feature](https://docs.pytest.org/en/7.1.x/how-to/mark.html) in Pytest. For example, the following will **skip** tests marked 'examples'.

=== "Using Docker Desktop"
`console
    pytest -k "not examples"
    `

=== "Using docker compose"
`console
    sudo docker compose -f docker-compose.dev-init.yml exec web pytest -k "not examples"
    `

## Verbosity

You can increase the [verbosity of the Pytest output](https://docs.pytest.org/en/7.1.x/how-to/output.html#verbosity) using the `-v` flag. The more `-v` flags you add, the more verbose the output, to a limit of -vv. The following will run the tests with the maximum verbosity.

=== "Using Docker Desktop"
`console
    pytest -vv
    `

=== "Using docker compose"
`console
    sudo docker compose -f docker-compose.dev-init.yml exec web pytest -vv
    `

## Running a single test

Pytest allows a specific test to be run by specifying the path to the test file. This can be useful when debugging a particular test. For example, the following will run only the test at the specified path.

=== "Using Docker Desktop"
`console
    pytest epilepsy12/tests/model_tests/test_antiepilepsy_medicine.py
    `

=== "Using docker compose"
`console
    sudo docker compose -f docker-compose.dev-init.yml exec web pytest epilepsy12/tests/model_tests/test_antiepilepsy_medicine.py
    `

To run a specific test within this file, use the `PATH_TO_TEST_FILE::TESTNAME` notation:

=== "Using Docker Desktop"
`console
    pytest epilepsy12/tests/model_tests/test_antiepilepsy_medicine.py::test_length_of_treatment
    `

=== "Using docker compose"
`console
    sudo docker compose -f docker-compose.dev-init.yml exec web pytest epilepsy12/tests/model_tests/test_antiepilepsy_medicine.py::test_length_of_treatment
    `

## Capturing `stdout` and `stderr`

If you have used `print()` statements in your code, you may want to capture the output of these statements in your tests. By default, Pytest captures the stdout from tests and displays them depending on certain conditions.

You can specify how stdout is displayed using the `-s` and/or `-rP` flags.

The `-rP` flag defines how Pytest shows the "short test summary info" content. It combines the `-r` option, which shows "failures and errors" by default, with `P`, which adds the captured output of passed tests.

=== "Using Docker Desktop"
`console
    pytest -rP
    `

=== "Using docker compose"
`console
    sudo docker compose -f docker-compose.dev-init.yml exec web pytest -rP
    `

The `-s` flag will tell Pytest to not capture the stdout and instead prints it straight to the console:

=== "Using Docker Desktop"
`console
    pytest -s
    `

=== "Using docker compose"
`console
    sudo docker compose -f docker-compose.dev-init.yml exec web pytest -s
    `

!!! tip "`pytest -h` for help"
Further details on the options available can be found by running `pytest -h` and visiting the [Pytest documentation](https://docs.pytest.org/).
