# epilepsy12-server

The EPILEPSY12 audit, as a backend, API and client-side

<p align="center">
    <img src="assets/epilepsy12-logo.jpg" width='200px'/>
</p>
<p align="center">
    <img align="center" src="assets/rcpch-logo.jpg" width='100px'/>
    <img align="center" src="assets/pmpc-logo.jpg" width='100px'/>
</p>

The project is part of the [Public Money Public Code](https://publicmoneypubliccode.org.uk/) community.

## Setup

If you don't have python 3.10 installed already, you will need it and [pyenv](https://github.com/pyenv/pyenv).

```console
foobar:~foo$ pyenv 3.10.0
```

If you have Homebrew, it does not always play well with pyenv and you might need first to:

```console
foobar:~foo$ brew install openssl readline sqlite3 xz zlib
```

You will also need [Postgresql](https://www.postgresql.org/)

Then create a virtual environment:

```console
foobar:~foo$ pyenv virtualenv 3.10.0 epilepsy12-server
```

Clone the repository:

```console
foobar:~foo$ git clone https://github.com/rcpch/epilepsy12-server.git
```

Then install all the requirements. Note you can't do this without Postgreql already installed.

```console
foobar:~foo$ pip install -r requirements/development-requirements
```

## Running the database

```console
foobar:~foo$ pg_ctl -D /usr/local/var/postgres -l logfile start
```

## Create the database

```console
foobar:~foo$ createdb epilepsy12-db
```

## Running the server

Navigate to the epilepsy12 outer folder and run the server:

```console
foobar:~foo$ python manage.py runserver
```
