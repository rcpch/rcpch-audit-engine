# rcpch-audit-engine

## National clinical audits, as a backend, API and client-side

### Designed and built by the RCPCH, by clinicians for clinicians.

<p align="center">
    <p align="center"></p>
    <p align="center">This project is part of the <a href="https://publicmoneypubliccode.org.uk/">Public Money Public Code</a> community.</p>
    <p align="center">
    <img align="center" src="./rcpch-audit-engine/epilepsy12/static/logo-block-outline-sm.png" width='100px'/>
    </p>
</p>

National clinical audits are there to collect diagnosis and care process data on patient cohorts with a diagnosis in common, nationally, to measure standard of care. They are a way to make sure that clinics are meeting centrally-set standards, and give clinics feedback on how they are doing.
National audits are commissioned by NHS England, and ensure all the data governance is in place, but the actual business of adminstering the audit and storing the data is usually contracted out. There is no standard for the way the data is stored or managed.

rcpch-audit-engine is a (Django)[https://www.djangoproject.com/] 4.0 project which aims to standards those elements of a national audit that can be standardised. It begins with Epilepsy12, a national audit for Childhood Epilepsies which has been in place since 2009.

## Epilepsy12

<p align="center">
    <img align="center" src="./rcpch-audit-engine/epilepsy12/static/epilepsy12-logo-1.png" width='100px'/>
</p>

### Setup

1. If you don't have python 3.10 installed already, you will need it and [pyenv](https://github.com/pyenv/pyenv).

```console
foobar:~foo$ pyenv 3.10.0
```

If you have Homebrew, it does not always play well with pyenv and you might need first to:

```console
foobar:~foo$ brew install openssl readline sqlite3 xz zlib
```

2. You will also need [Postgresql](https://www.postgresql.org/)

3. Then create a virtual environment:

```console
foobar:~foo$ pyenv virtualenv 3.10.0 epilepsy12-server
```

4. Clone the repository:

```console
foobar:~foo$ git clone https://github.com/rcpch/epilepsy12-server.git
```

5. Then install all the requirements. Note you can't do this without Postgreql already installed.

```console
foobar:~foo$ pip install -r requirements/development-requirements
```

### Running the database

We advise running the postgresql database from within Docker on port 5432, the default for Django

```command
foobar:~foo$ docker build
```

## Create the database

```console
foobar:~foo$ createdb epilepsy12-db
```

## Prepare the database for use

```console
foobar:~foo$ start/migrate
```

## Running the server

Navigate to the epilepsy12 outer folder and run the server:

```console
foobar:~foo$ start/runserver
```

or

you may need to allow permissions to run the bash script in that folder first:

```console
foobar:~foo$ chmod +x ./start/runserver
```