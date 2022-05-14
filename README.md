# Designed and built by the RCPCH, by clinicians for clinicians

<p align="center">
    <p align="center"></p>
    <p align="center">This project is part of the <a href="https://publicmoneypubliccode.org.uk/">Public Money Public Code</a> community.</p>
    <p align="center">
    <img align="center" src="epilepsy12/static/logo-block-outline-sm.png" width='100px'/>
    </p>
</p>

National clinical audits are there to collect diagnosis and care process data on patient cohorts with a diagnosis in common, nationally, to measure standard of care. They are a way to make sure that clinics are meeting centrally-set standards, and give clinics feedback on how they are doing. National audits are commissioned by NHS England.

`rcpch-audit-engine` is a [Django](https://www.djangoproject.com/) 4.0 project which aims to standardise those elements of a national audit that can be standardised. It begins with Epilepsy12, a national audit for Childhood Epilepsies which has been in place since 2009.

## rcpch-audit-engine

A framework for national clinical audits. Built using Django and Semantic UI.

Initially intended as a new platform for the RCPCH's established Epilepsy12 audit, but designed so as to be usable for other audits.

### Epilepsy12

<p align="center">
    <img align="center" src="epilepsy12/static/epilepsy12-logo-1.png" width='100px'/>
</p>

[![DOI](https://zenodo.org/badge/415328052.svg)](https://zenodo.org/badge/latestdoi/415328052)

#### Setup

If you don't have python 3.10 installed already, you will need it. We recommend the use of a tool such as [pyenv](https://github.com/pyenv/pyenv) to assist with managing multiple Python versions and their accompanying Virtualenvs.

```console
$ pyenv install 3.10.0
```

> On some platforms, you will get errors at build-time, which indicates you need to install some dependencies which are required for building the Python binaries locally. Rather than listing these here, where they may become out of date, please refer to the [pyenv wiki](https://github.com/pyenv/pyenv/wiki) which covers this in detail.



You will also need the [Postgresql](https://www.postgresql.org/) database, which can be installed natively on your development machine, or can be installed using Docker.

Then create a virtual environment:

```console
(python-3.10) ➜  ~ pyenv virtualenv 3.10.0 rcpch-audit-engine
```

Clone the repository and `cd` into the directory:

```console
(rcpch-audit-engine) ➜  ~ git clone https://github.com/rcpch/rcpch-audit-engine.git
(rcpch-audit-engine) ➜  ~ cd rcpch-audit-engine
```

Then install all the requirements. Note you can't do this without PostgreSQL already installed.

```console
(rcpch-audit-engine) ➜  ~ pip install -r requirements/development-requirements.txt
```

#### Create the database

```command
docker run --name epilepsy12postgres -e POSTGRES_USER=epilepsy12user -e POSTGRES_PASSWORD=epilepsy12 -e POSTGRES_DB=epilepsy12db -p 5432:5432 -d postgres
```

#### Initialize the environment variables

```console
source example.env
```

#### Prepare the database for use

```console
s/migrate
```

#### Create superuser to enable logging into admin section

```console
python manage.py createsuperuser
```

Then follow the command line prompts to create the first user

Further users can subsequently be created in the Admin UI

#### Running the server

Navigate to the epilepsy12 outer folder and run the server:

```console
s/runserver
```

or

you may need to allow permissions to run the bash script in that folder first:

```console
chmod +x ./s
```

#### Seeding the Database

You will need to see the hospitals table with hospitals from the Constants folder.

```console
python manage.py seed_hospitals
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

#### Testing (optional step)

We have used the coverage package to test our models.

```console
pip install coverage
coverage run manage.py test
coverage html
```

If the ```htmlcov/index.html``` is opened in the browser, gaps in outstanding testing of the models can be found.

### Stated Aims of the Audit

* Continue to measure and improve care and outcomes for children and young people with
epilepsies
* Include all children and young people with a new onset of epilepsy,
* Enable continuous patient ascertainment,
* Use a pragmatic and concise dataset,
* Incorporate NICE Quality Standards alongside metrics about mental health, education and
transition to adult services,
* Provide services with local real-time patient- and service-level reporting.

#### Quality Improvement

* Supporting regional and national quality improvement activities
* Epilepsy Quality Improvement Programme (EQIP)
* Involving children and young people

#### There are 12 key performance indicators

1. Input into care from a paediatrician with expertise in epilepsies,
2. Input into care from an epilepsy specialist nurse (ESNs),
3. (a) Appropriate tertiary input into care, and  
   (b) appropriate epilepsy surgery referral
4. Appropriate first paediatric assessment,
5. Recorded seizure formulation,
6. Access to electrocardiogram (ECG),
7. Access to magnetic resonance imaging (MRI),
8. Accuracy of diagnosis,
9. (a) Discussion of the risks where sodium valproate is used in treatment for girls aged 9 and over,
and  
(b) girls and young women prescribed sodium valproate
10. Comprehensive care plan that is updated and agreed with the patient,
11. Documented evidence of all key elements of care planning content,
12. Record of a school individual healthcare plan.

#### Schema

Main classes - these are all found in the epilepsy12/models folder*

* The Case class records information about each young person
* The Registration class holds a record for each audit.
* The Assessment class holds information on cases gathered over the one year audit period.
* The InitialAssessment class is closely linked to Assessment and holds the minimum expected information collected at first assessment.  
* The Investigations class records dates that initial tests were recorded (ECG, EEG, CT and MRI)
* The EpilepsyContext class records contextual information that defines epilepsy risk.
* The Comorbidity class records information on emotional, behavioural, neurodevelopmental and neuropsychatric comorbidities

* The RescueMedicine class records information on rescue medicines used.
* The AntiEpilepsyDrug class records information about antiepilepsy drugs.

* The SeizureType class describes the seizure type.
* The ElectroClinicalSydrome class records information on electroclinical syndromes.
* The SeizureCause class records the cause of each seizure.
* The NonEpilepsy class records information about nonepilepsy features of episode.

* The Site class records information about each site that oversees the epilepsy care of each case.
* The HospitalTrust class records hospital trust details. It is used as a look up class for the Site class.

#### Relationships

* Case to Registration 1:1  
* Case to Site 1:n  
* Case to Comorbidity n:n

* Registration to Assessment 1:1
* Registration to InitialAssessment 1:1
* Registration to EpilepsyContext  1:1

* Comorbidity to EpilepsyContext 1:n

* Registration to Investigations 1:1
* Registration to RescueMedicine 1:1
* Registration to ElectroClinicalSyndrome 1:1
* Registration to SeizureCause 1:1
* Registration to SeizureType 1:1
* Registration to AntiEpilepsyDrug 1:1
* Registration to RescueMedicine 1:1
* Registration to NonEpilepsy 1:1

* HospitalTrust to Site 1:n
