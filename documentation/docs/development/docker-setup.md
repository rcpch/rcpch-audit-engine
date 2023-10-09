---
title: Docker development
reviewers: Dr Marcus Baw, Dr Simon Chapman, Dr Anchit Chandran
---

To simplify the development environment setup and provide greater consistency between development and production environments, the application is built as a Docker image and `docker compose` sets up the other necessary containers in development.

This means you don't need to worry about conflicts of Python versions, Python library versions, or Python virtual environments. Everything is specified and isolated inside the Docker containers.

## Setup for development using Docker Compose

1. Install Docker on your development machine. Instructions for all platforms are at [:fontawesome-brands-docker: get-docker](https://docs.docker.com/get-docker)

1. Clone the Audit Engine repository to your code folder:

    ```console
    git clone https://github.com/rcpch/rcpch-audit-engine.git
    ```

1. Navigate into the folder

    ```console
    cd rcpch-audit-engine
    ```

    !!! warning "Windows Setup"
        **If you are on Windows**, after installing Docker and cloning the repository, please now skip to the [(Windows) Setup for development using Docker Compose](./docker-setup.md#windows-setup-for-development-using-docker-compose) section.

1. Ensure you are on the default `development` branch

    ```console
    git checkout post-documentation-combine-tidying
    ```

1. Obtain a `.env` file containing the required environment files.

    These files contain credentials and secrets and therefore the `.env` files themselves are **never** committed to version control. All `*.env` files are `.gitignore`'d.

    If you work with the RCPCH Incubator team, another member of the team may be able to supply you with a completed `local-dev.env` file.

    For anyone else, there is a template environment file in the repository root which you can rename to `local-dev.env` and use as a starting point.

    ```console
    mv envs/env-template envs/local-dev.env
    ```

1. Start the development environment for the first time using our startup script

    ```console
    s/docker-up
    ```

    This script automates all the setup steps including upgrading `pip`, installing all development dependencies with `pip install`, migrating the database, seeding the database, and creating a superuser.

`s/docker-up` will build the necessary Docker images, create the containers, and start them up. There will be a lot of output in the terminal, but it should create a number of containers and network them together. If you hit errors, please do open an issue.

At the end of the terminal output you should see something like:

```console
rcpch-audit-engine-web-1          | Django version 4.2.5, using settings 'rcpch-audit-engine.settings'
rcpch-audit-engine-web-1          | Starting development server at http://0.0.0.0:8000/
rcpch-audit-engine-web-1          | Quit the server with CONTROL-C.
```

View the application in a browser at <http://0.0.0.0:8000/> and login using the credentials above.

Changes you make in your development folder are **automatically synced to inside the Docker container**, and will show up in the application right away.

This Docker setup is quite new so please do open an issue if there is anything that doesn't seem to work properly. Suggestions and feature requests welcome.

## (Windows) Setup for development using Docker Compose

You should have already [downloaded Docker](https://docs.docker.com/get-docker/) and cloned the repository.

### Enabling the WSL Terminal within VS Code

There are scripts in the `s/` which streamline the setup for the development process. Unfortunately, Windows does not natively support running these through the Command Prompt. Instead, we must first install the **Windows Subsystem for Linux (WSL)** to run the scripts.

VS Code has a helpful extension to do just this!

Follow this guide ([Windows Subsystem for Linux VSCode Extension](https://code.visualstudio.com/docs/remote/wsl-tutorial)) to enable usage of a *Ubuntu (WSL)* terminal within VS Code.

### Running Scripts

Open a new WSL terminal by selecting it:

![Screenshot of WSL Terminal in VS Code](../_assets/_images/windev_wsl_terminal.png)

If you haven't already, `cd` into the root folder

```console
cd rcpch-audit-engine/
```

Finally, you should be able to run the setup script by typing:

```console
sh s/docker-up
```

!!! info "Setup errors"
    Sometimes, the easiest fix for many headaches, relating to installation and setup, is to simply restart your computer and try again!

### What does `s/docker-up` do?

This script automates all the setup steps including:

- upgrading `pip`
- installing all development dependencies with `pip install`
- migrating the database
- seeding the database
- creating a superuser

> Development superuser credentials are: username: `e12-dev-user@rcpch.tech` and password `pw`.
> <br> **Note these insecure default credentials are ONLY ever used in development for simplicity and ease of use and NEVER used in testing/staging or live.**


The django container is built with the correct Python version, all development dependencies are automatically installed, the database connection is created, migrations applied and seed data added to the database. The entire process takes less than 30 seconds.

View the application in a browser at <http://localhost:8000/> and login using the credentials above.

Changes you make in your development folder are automatically synced to inside the Docker container, and will show up in the application right away.

This Docker setup is quite new so please do open an issue if there is anything that doesn't seem to work properly. Suggestions and feature requests welcome.

## Executing commands in the context of the `django` container

You can run commands in the context of any of the containers using `docker compose`.

The below command will execute `<command>` inside the `django` container.

```console
docker compose -f docker-compose.yml exec django <command>
```

For example, to create a superuser

```console
sudo docker compose -f docker-compose.yml exec django python manage.py createsuperuser
```

!!! warning "Inactive Terminal"
    If you have successfully opened a Docker container for the engine, your Terminal will no longer show an interactive prompt, which is means you cannot run commands in that Terminal. To resolve this, simply **open another Terminal window**


## Running the test suite

```console
s/docker-test
```

## Shutting down the Docker Compose environment

++ctrl+c++ will shut down the containers but will leave them built. You can restart them rapidly with `s/docker-up`.

To shut down and destroy the containers so that you can start again from scratch (for example if you want to rebuild and re-seed the database) then use

```console
s/docker-down
```

## Tips and Tricks

* Although the `docker compose` setup is very convenient, and it installs all the runtime development dependencies _inside_ the `django` container, one thing it can't do is install any _local_ Python packages which are required for text editing, linting, and similar utilities _outside_ the container. Examples are `pylint`, `pylint_django`, etc. You will still need to install these locally, ideally in a virtual environment.
