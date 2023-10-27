---
reviewers: Dr Anchit Chandran
---

## Descriptive Test Function Names

Tests should have clear and descriptive names conveying purpose. This improves the readability of the test suite.

## Test independence and isolation

Tests should be independent, never relying on the outcomes of other tests.

## Unit vs Integration Tests

Unit tests focus on testing individual components in isolation, such as Model Tests.

Integration tests focus on interactions between multiple components, such as the `calculate_kpi` tests.

## New code needs new tests

Ideally, following Test-Driven-Development practice, tests should be written *before* the code is written.

All new code requires tests to be written to be confident of functionality, and prevent future regressions.

New PRs must pass all tests.
