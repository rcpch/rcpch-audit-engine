# rcpch-audit-engine

## National clinical audits, as a backend, API and client-side

### Designed and built by the RCPCH, by clinicians for clinicians

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
foobar:~foo$ pyenv install 3.10.0
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

### Create the database

```command
foobar:~foo$ docker run --name E12_Container -e POSTGRES_USER=epilepsy12user -e POSTGRES_PASSWORD=epilepsy12 -e POSTGRES_DB=epilepsy12db -p 5432:5432 -d postgres
```

## Prepare the database for use

```console
foobar:~foo$ s/migrate
```

## Create a super user

```console
foobar:~foo$ python manage.py createsuperuser
```

## Running the server

Navigate to the epilepsy12 outer folder and run the server:

```console
foobar:~foo$ s/runserver
```

or

you may need to allow permissions to run the bash script in that folder first:

```console
foobar:~foo$ chmod +x ./s/runserver
```

## Create superuser to enable logging into admin section

```console
python manage.py createsuperuser
```

Then follow the command line prompts to create the first user

Further users can subsequently be created in the Admin UI

##  Stated Aims of the Audit

* Continue to measure and improve care and outcomes for children and young people with
epilepsies
* Include all children and young people with a new onset of epilepsy,
* Enable continuous patient ascertainment,
* Use a pragmatic and concise dataset,
* Incorporate NICE Quality Standards alongside metrics about mental health, education and
transition to adult services,
* Provide services with local real-time patient- and service-level reporting.

### Quality Improvement

* Supporting regional and national quality improvement activities
* Epilepsy Quality Improvement Programme (EQIP)
* Involving children and young people

### There are 12 key performance indicators:

1. Input into care from a paediatrician with expertise in epilepsies,
2. Input into care from an epilepsy specialist nurse (ESNs),
3. (a) Appropriate tertiary input into care, and (b) appropriate epilepsy surgery referral
4. Appropriate first paediatric assessment,
5. Recorded seizure formulation,
6. Access to electrocardiogram (ECG),
7. Access to magnetic resonance imaging (MRI),
8. Accuracy of diagnosis,
9. (a) Discussion of the risks where sodium valproate is used in treatment for girls aged 9 and over,
and (b) girls and young women prescribed sodium valproate
10. Comprehensive care plan that is updated and agreed with the patient,
11. Documented evidence of all key elements of care planning content,
12. Record of a school individual healthcare plan.

## Schema

Main classes - these are all found in the epilepsy12/models folder*

The Case class records information about each young person
The Registration class holds a record for each audit.
The Assessment class holds information on cases gathered over the one year audit period.
The InitialAssessment class is closely linked to Assessment and holds the minimum expected information collected at first assessment.  
The Investigations class records dates that initial tests were recorded (ECG, EEG, CT and MRI)
The EpilepsyContext class records contextual information that defines epilepsy risk.
The Comorbidity class records information on emotional, behavioural, neurodevelopmental and neuropsychatric comorbidities

The RescueMedicine class records information on rescue medicines used.
The AntiEpilepsyDrug class records information about antiepilepsy drugs.

The SeizureType class describes the seizure type.
The ElectroClinicalSydrome class records information on electroclinical syndromes.
The SeizureCause class records the cause of each seizure.
The NonEpilepsy class records information about nonepilepsy features of episode.

The Site class records information about each site that oversees the epilepsy care of each case.
The HospitalTrust class records hospital trust details. It is used as a look up class for the Site class.


## Relationships

Case to Registration 1:1
Case to Site 1:n
Case to Comorbidity n:n

Registration to Assessment 1:1
InitialAssessment to Assessment 1:1
InitialAssessment to EpilepsyContext  1:1

Comorbidity to Case n:n

Assessment to Investigations n:n
Assessment to RescueMedicine 1:n
Assessment to ElectroClinicalSyndrome 1:1
Assessment to SeizureCause n:n
Assessment to SeizureType 1:n
Assessment to AntiEpilepsyDrug n:n
Assessment to RescueMedicine n:n
Assessment to NonEpilepsy 1:1

HospitalTrust to Site 1:n