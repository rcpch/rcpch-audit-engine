---
title: Testing
reviewers: Dr Marcus Baw, Dr Anchit Chandran
---

Tests for the Epilepsy12-specific parts of the platform are organised in an `epilepsy12/tests/` folder inside the epilepsy12 app. We have opted to use Pytest, which is well-regarded in the Django community.

## Running `pytest`

When running tests, it is important to understand that they will only run **inside** the Docker container (assuming you have used the Docker development setup). Therefore, how you run the tests depends on whether you are using Docker Desktop (either through the native application or [VSCode extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) where you can attach a shell terminal to the Docker environment) or Docker Compose. The following examples assume you are at the root of the project.

=== "Using Docker Desktop"
    Using the [integrated terminal](https://docs.docker.com/desktop/use-desktop/container/#integrated-terminal) in Docker Desktop:
    ```console
    pytest
    ```

=== "Using docker compose"
    Run the following command in your normal system terminal:
    ```console
    sudo docker compose -f docker-compose.dev-init.yml exec web pytest
    ```
