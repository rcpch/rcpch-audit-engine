---
title: Manual dev setup
reviewers: Dr Marcus Baw
---

If you prefer to set up a development environment manually, here are the steps. Please note that we do not provide support for developers using a bespoke setup, only the Docker development environment is supported.

This manual approach will require you to have much more familiarity with configuring PostgresQL, Django, and Python to achieve your aims, and is not for beginners.

## Install PostgreSQL and create the database with the correct credentials

You will need the [Postgresql](https://www.postgresql.org/) database, which can be installed natively on your development machine, or (recommended) can be installed using Docker.

Using the command below will create a development database with credentials that match those in our `example.env` file.  
You will need Docker to be installed on your local machine. (Please search the web for instructions for installation on your operating system and setup)

```console
docker run --name epilepsy12postgres \
    -e POSTGRES_USER=epilepsy12user \
    -e POSTGRES_PASSWORD=epilepsy12 \
    -e POSTGRES_DB=epilepsy12db \
    -p 5432:5432 \
    -d postgres
```

## Install the correct Python version

If you don't have python 3.10 installed already, you will need it.

We recommend the use of a tool such as [pyenv](https://github.com/pyenv/pyenv) to assist with managing multiple Python versions and their accompanying virtualenvs.

```console
pyenv install 3.10.0
```

> On some platforms, you will get errors at build-time, which indicates you need to install some dependencies which are required for building the Python binaries locally. Rather than listing these here, where they may become out of date, please refer to the [pyenv wiki](https://github.com/pyenv/pyenv/wiki) which covers this in detail.

Then create a virtual environment:

```console
pyenv virtualenv 3.10.0 rcpch-audit-engine
```

Clone the repository and `cd` into the directory:

```console
git clone https://github.com/rcpch/rcpch-audit-engine.git
cd rcpch-audit-engine
```

Then install all the requirements. Note you can't do this without PostgreSQL already installed first.

```console
pip install -r requirements/development-requirements.txt
```

## Initialize the environment variables

```console
source example.env
```

!!! danger
The included example environment variables are not secure and must never be used in production.

## Prepare the database for use

```console
s/migrate
```

## Create superuser to enable logging into admin section

```console
python manage.py createsuperuser
```

Then follow the command line prompts to create the first user

Further users can subsequently be created in the Admin UI

## Running the server

Navigate to the epilepsy12 outer folder and run the server:

```console
s/runserver
```

or

you may need to allow permissions to run the bash script in that folder first:

```console
chmod +x ./s/runserver
chmod +x ./s/migrate
chmod +x ./s/seed
chmod +x ./s/init
```

## Seeding the Database

You will need to see the hospitals table with hospitals from the Constants folder.

```console
python manage.py seed --mode=seed_hospitals
```

If you need to delete all the hospitals:

```console
python manage.py seed --mode=delete_hospitals
```

To add the semiology keywords to the database:

```console
python manage.py seed --mode=seed_semiology_keywords
```

To add the some dummy cases to the database:

```console
python manage.py seed --mode=seed_dummy_cases
```

If you want to seed with all these, there is a short cut in the start folder:

```console
s/seed
```

## Running the tests locally

We have used the coverage package to test our models. It is already in our development requirements, but if you don't have it installed, install it with `pip install coverage`

Run all the tests

```console
coverage run manage.py test
coverage html
```

If the `htmlcov/index.html` is opened in the browser, gaps in outstanding testing of the models can be found.
