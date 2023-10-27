---
title: Docker development
reviewers: Dr Marcus Baw, Dr Simon Chapman, Dr Anchit Chandran
---

To simplify the development environment setup and provide greater consistency between development and production environments, the application is built as a Docker image and Docker Compose sets up the other necessary containers in development.

This means you don't need to worry about conflicts of Python versions, Python library versions, or Python virtual environments. Everything is specified and isolated inside the Docker containers.

## Setup for development using Docker Compose

### Install Docker on your development machine.

Instructions for all platforms are at [:fontawesome-brands-docker: get-docker](https://docs.docker.com/get-docker)

### Clone the Audit Engine repository to your code folder:

```console
git clone https://github.com/rcpch/rcpch-audit-engine.git
```

### Navigate into the folder

```console
cd rcpch-audit-engine
```

!!! warning "Windows Setup"
    **If you are on Windows**, after installing Docker and cloning the repository, please now skip to the [(Windows) Setup for development using Docker Compose](./docker-setup.md#windows-setup-for-development-using-docker-compose) section.

### Ensure you are on the default `development` branch

```console
git checkout development
```

### Obtain a `.env` file containing the required environment files.

These files contain credentials and secrets and therefore the `.env` files themselves are **never** committed to version control. All `*.env` files are `.gitignore`'d, as is the entire contents of the `envs/` folder except the env_template file.

If you work with the RCPCH Incubator team, another member of the team may be able to supply you with a completed `.env` file.

For anyone else, there is a template environment file in the repository root which you can rename to `.env` and use as a starting point. **Be extremely careful to make sure it is named `.env` so that it is ignored by Git. Do not ever commit `.env` files to version control!**

```console
cp envs/env-template envs/.env
```

### Start the development environment for the first time using our startup script

```console
s/docker-up
```

This script automates all the setup steps including upgrading `pip`, installing all development dependencies with `pip install`, migrating the database and seeding the database with some essential data.

### Trust the Caddy root CA certificate

To get a HTTPS connection through the Caddy server to work on `e12.localhost`, you need to trust the Caddy root CA certificate. This is only necessary once.

Instructions for this are in the [Caddy documentation](https://caddyserver.com/docs/running#local-https-with-docker)

With some browsers you may need to manually add the certificate in the Security settings, see the above link for details. Restart the browser after trusting the certificate.

`s/docker-up` will build the necessary Docker images, create the containers, and start them up. There will be a lot of output in the terminal, but it should create a number of containers and network them together. If you hit errors, please do open an issue.

At the very end of the terminal output, which could take several minutes, you should see something like this:

```console
rcpch-audit-engine-web-1          | Django version 4.2.5, using settings 'rcpch-audit-engine.settings'
rcpch-audit-engine-web-1          | Starting development server at http://0.0.0.0:8000/
rcpch-audit-engine-web-1          | Quit the server with CONTROL-C.
```

!!! warning "<https://e12.localhost>, not <http://localhost:8000>"
    **IMPORTANT: Because we are using the Caddy web server as a reverse proxy, the application should be accessed at <https://e12.localhost>, not <http://localhost:8000>, even though Django will still report that is the hostname and port it 'thinks' it is listening on.**

Changes you make in your development folder are **automatically synced to inside the Docker container**, and will show up in the application right away.

This Docker setup is quite new so please do open an issue if there is anything that doesn't seem to work properly. Suggestions and feature requests welcome.

### What does `s/docker-up` do?

This script automates all the setup steps including:

- upgrading `pip`
- installing all development dependencies with `pip install`
- migrating the database
- seeding the database

The `django` container is built with the correct Python version, all development dependencies are automatically installed, the database connection is created, migrations applied and some seed data is added to the database.

View the application in a browser at <e12.localhost>.

Changes you make in your development folder are automatically synced to inside the Docker container, and will show up in the application right away.

This Docker setup is quite new so please do open an issue if there is anything that doesn't seem to work properly. Suggestions and feature requests welcome.

## Executing commands in the context of the `django` container

You can run commands in the context of any of the containers using Docker Compose.

The below command will execute `<command>` inside the `django` container.

```console
docker compose exec django <command>
```

For example, to create a superuser

```console
sudo docker compose exec django python manage.py createsuperuser
```

!!! warning "Terminal is now occupied"
    If you have successfully run the Docker Compose deployment, your terminal will be showing the logging output for all the containers and will no longer show an interactive prompt, which is means you can not run any more commands in that terminal. To resolve this, simply **open another Terminal window** in the same working directory, in which you can run commands.

## Running the test suite

```console
s/docker-test
```

This will execute our suite of Pytest tests inside the `django` container, and the output should be displayed in the console for you.

## Shutting down the Docker Compose environment

++ctrl+c++ will shut down the containers but will leave them built. This means you can restart them rapidly with `s/docker-up`.

To shut down all containers use

```console
s/docker-down
```

To shut down **and destroy the containers and the images** they are built from, use

```console
s/docker-down-rm-containers-images
```

To go even further and **delete all the data of the application**, including the database, use

```console
s/docker-delete-local-data
```

For obvious reasons this is something that should ONLY be done in local development environments.

## Tips and Tricks, Gotchas and Caveats

* Although the Docker Compose setup is very convenient, and it installs all the runtime development dependencies _inside_ the `django` container, one thing it can't do is install any _local_ Python packages which are required for text editing, linting, and similar utilities _outside_ the container. Examples are `pylint`, `pylint_django`, etc. You will still need to install these locally, ideally in a virtual environment using `pyenv`.
