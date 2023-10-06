---
title: Coverage
reviewers: Dr Anchit Chandran
---

Using the `coverage` tool, we can get some code analysis, including the total test coverage. For example, the following will run pytest through `coverage`. Then type `coverage report` to see the coverage report.

=== "Using Docker Desktop"
    ```console
    coverage run -m pytest
    coverage report
    ```

=== "Using docker compose"
    ```console
    sudo docker compose -f docker-compose.dev-init.yml exec web coverage run -m pytest
    sudo docker compose -f docker-compose.dev-init.yml exec web coverage report
    ```
    