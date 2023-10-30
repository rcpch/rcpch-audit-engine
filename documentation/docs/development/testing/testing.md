---
title: Testing
reviewers: Dr Marcus Baw, Dr Anchit Chandran, Dr Baribefe O Vite
---

Tests for the Epilepsy12-specific parts of the platform are organised in an `epilepsy12/tests/` folder inside the epilepsy12 app. We have opted to use Pytest, which is well-regarded in the Django community.

!!! warning "Active Docker Container"
    Please ensure that your Docker container is still built and active. The previous command in the 'Docker setup' page was to illustrate how to close the Docker container. To reopen it, run:
    ```console
    s/docker-up
    ```

## Running `pytest`

When running tests, it is important to understand that they will only run **inside** the Docker container (assuming you have used the Docker development setup). Therefore, how you run the tests depends on whether you are using Docker Desktop (either through the native application or [VSCode extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) where you can attach a shell terminal to the Docker environment) or Docker Compose. The following examples assume you are at the root of the project.

=== "Using Docker Desktop"
    Using the [integrated terminal](https://docs.docker.com/desktop/use-desktop/container/#integrated-terminal) in Docker Desktop:
    ```console
    pytest
    ```

=== "Using s/docker scripts "
    Run the following command in your normal system terminal:
    ```console
    s/docker-test
    ```
