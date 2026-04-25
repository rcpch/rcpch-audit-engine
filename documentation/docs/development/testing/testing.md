---
title: Testing
reviewers: Dr Marcus Baw, Dr Anchit Chandran, Dr Baribefe O Vite
---

Tests for the Epilepsy12-specific parts of the platform are organised in an `epilepsy12/tests/` folder inside the epilepsy12 app. We have opted to use Pytest, which is well-regarded in the Django community.

!!! warning "Active Docker Container"
    Please ensure that your Docker container is still built and active. The previous command in the 'Docker setup' page was to illustrate how to close the Docker container. To reopen it, run:
    ```console
    s/up
    ```

## Running `pytest`

When running tests, there are three common modes: directly on the host, in a running `django` container, or in a temporary test-only Docker Compose project. The following examples assume you are at the root of the project.

=== "Using Docker Desktop"
    Using the [integrated terminal](https://docs.docker.com/desktop/use-desktop/container/#integrated-terminal) in Docker Desktop:
    ```console
    pytest
    ```

=== "Using s/docker scripts "
    Run the following command in your normal system terminal:
    ```console
    s/test
    ```

- `s/test` runs pytest in the django container (default).
- `s/test --local` (or `--host`) runs pytest directly on the host.
- `s/test --spin-up` (or `--up`) spins up an isolated test-only compose project, runs pytest in `django`, then tears it down.
