# python
from operator import itemgetter
from random import randint, choice
from datetime import date
from dateutil.relativedelta import relativedelta
from random import randint
from django.core.management.base import BaseCommand


from ...constants import ETHNICITIES, DUMMY_NAMES, SYNDROMES, SNOMED_BENZODIAZEPINE_TYPES, SNOMED_ANTIEPILEPSY_MEDICINE_TYPES, RCPCH_ORGANISATION_CODES
from ...models import Organisation, Keyword, Case, Site, Registration, SyndromeEntity, EpilepsyCauseEntity, ComorbidityEntity, MedicineEntity, AntiEpilepsyMedicine
from ...constants import ALL_HOSPITALS, KEYWORDS, WELSH_HOSPITALS
from ...general_functions import random_postcodes, random_date, first_tuesday_in_january, current_cohort_start_date, fetch_ecl, fetch_paediatric_neurodisability_outpatient_diagnosis_simple_reference_set, fetch_ods
from .create_groups import create_groups, add_permissions_to_existing_groups, delete_and_reallocate_permissions
from .create_e12_records import create_epilepsy12_record, create_registrations
from .add_codes_to_organisations import add_codes_to_organisation


class Command(BaseCommand):
    help = "seed database with organisation trust data for testing and development."

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help="Mode")

    def handle(self, *args, **options):
        if (options['mode'] == 'delete_organisations'):
            self.stdout.write('Deleting organisation trust data...')
            delete_organisations()
        elif (options['mode'] == 'seed_organisations'):
            self.stdout.write('seeding organisation data...')
            run_organisations_seed()
        elif (options['mode'] == 'seed_welsh_organisations'):
            self.stdout.write('seeding organisation data...')
            run_welsh_organisations_seed()
        elif (options['mode'] == 'add_codes_to_english_organisations'):
            self.stdout.write(
                'adding ODS codes to existing English organisation records...')
            add_codes_to_english_organisations()
        elif (options['mode'] == 'seed_semiology_keywords'):
            self.stdout.write('seeding organisation data...')
            run_semiology_keywords_seed()
        elif (options['mode'] == 'seed_syndromes'):
            self.stdout.write('seeding syndromes...')
            run_syndromes_seed()
        elif (options['mode'] == 'seed_epilepsy_causes'):
            self.stdout.write('seeding epilepsy causes...')
            run_epilepsy_causes_seed()
        elif (options['mode'] == 'seed_comorbidities'):
            self.stdout.write('seeding comorbidities...')
            run_comorbidities_seed()
        elif (options['mode'] == 'seed_medicines'):
            self.stdout.write('seeding medicines...')
            run_medicines_seed()
        elif (options['mode'] == 'seed_dummy_cases'):
            self.stdout.write('seeding with dummy case data...')
            run_dummy_cases_seed()
        elif (options['mode'] == 'seed_registrations'):
            self.stdout.write(
                'register cases in audit and complete all fields with random answers...')
            run_registrations()
        elif (options['mode'] == 'seed_groups_and_permissions'):
            self.stdout.write('setting up groups and permissions...')
            create_groups()
        elif (options['mode'] == 'add_permissions_to_existing_groups'):
            self.stdout.write('adding permissions to groups...')
            add_permissions_to_existing_groups()
        elif (options['mode'] == 'delete_all_groups_and_recreate'):
            self.stdout.write(
                'deleting all groups/permissions and reallocating...')
        elif (options['mode'] == 'replace_comorbidities_with_refset'):
            self.stdout.write(
                'replacing comorbidites with refset...')
            replace_existing_comorbidities_with_refset()
        elif (options['mode'] == 'add_existing_medicines_as_foreign_keys'):
            self.stdout.write(
                'replacing medicines with medicine entity...')
        elif (options['mode'] == 'update_medicine_entity_with_snomed'):
            self.stdout.write(
                'updating medicine_entities with SNOMED...')
            update_medicine_entity_with_snomed()

        else:
            self.stdout.write('No options supplied...')
        print('\033[38;2;17;167;142m')
        self.stdout.write(image())
        print('\033[38;2;17;167;107m')
        self.stdout.write('done.')


def run_syndromes_seed():
    added = 0
    for syndrome in sorted(SYNDROMES, key=itemgetter(1)):
        if SyndromeEntity.objects.filter(syndrome_name=syndrome[1]).exists():
            print(
                f'Syndromes already exist. Skipping this step...')
            return
        new_syndrome = SyndromeEntity(
            syndrome_name=syndrome[1],
            snomed_ct_code=None,
            icd_10_code=None,
            icd_10_name=None
        )
        try:
            new_syndrome.save()
        except Exception as e:
            print(f"Error at {syndrome[1]}: error: {e}")
        added += 1
        print(
            f"added {syndrome[1]}")
    print(f"Syndromes added...{added}")


def run_semiology_keywords_seed():
    added = 0
    for index, semiology_keyword in enumerate(KEYWORDS):
        if Keyword.objects.filter(keyword=semiology_keyword["title"]).exists():
            print(
                f'Keywords already exist. Skipping this step...')
            return
        new_keyword = Keyword(
            keyword=semiology_keyword["title"],
            category=semiology_keyword["category"]
        )
        try:
            new_keyword.save()
        except Exception as e:
            print(f"Error at {semiology_keyword['title']}: error: {e}")
        added += 1
        print(
            f"added {semiology_keyword['title']} in category {semiology_keyword['category']}")
    image()
    print(f"Keywords added: {added}")


def run_epilepsy_causes_seed():
    """
    This returns all the snomed ct definitions and codes for epilepsy causes.
    Should be run periodically to compare with value in database and update record if has changed
    """
    if EpilepsyCauseEntity.objects.count() > 0:
        print('Causes already exist. Skipping this step...')
        return
    index = 0
    ecl = '<< 363235000'
    # calls the rcpch deprivare server for a list of causes using ECL query language
    epilepsy_causes = fetch_ecl(ecl)
    for cause in epilepsy_causes:
        new_cause = EpilepsyCauseEntity(
            conceptId=cause['conceptId'],
            term=cause['term'],
            preferredTerm=cause['preferredTerm'],
            description=None,
            snomed_ct_edition=None,
            snomed_ct_version=None,
            icd_code=None,
            icd_version=None,
            dsm_code=None,
            dsm_version=None
        )
        try:
            new_cause.save()
            index += 1
        except Exception as e:
            print(f"Epilepsy cause {cause['preferredTerm']} not added. {e}")
    print(f"{index} epilepsy causes added")


def run_comorbidities_seed():
    """
    This returns all the snomed ct definitions and codes for epilepsy causes.
    Should be run periodically to compare with value in database and update record if has changed
    """
    if ComorbidityEntity.objects.count() > 0:
        print('Comorbidities already exist. Skipping...')
        return
    index = 0
    # ecl = '<< 35919005'
    # comorbidity_choices = fetch_ecl(ecl)
    comorbidity_choices = fetch_paediatric_neurodisability_outpatient_diagnosis_simple_reference_set()

    for comorbidity_choice in comorbidity_choices:
        new_comorbidity = ComorbidityEntity(
            conceptId=comorbidity_choice['conceptId'],
            term=comorbidity_choice['term'],
            preferredTerm=comorbidity_choice['preferredTerm'],
            description=None,
            snomed_ct_edition=None,
            snomed_ct_version=None,
            icd_code=None,
            icd_version=None,
            dsm_code=None,
            dsm_version=None,
        )
        try:
            new_comorbidity.save()
            index += 1
        except Exception as e:
            print(
                f"Comorbidity {comorbidity_choice.preferredTerm} not added. {e}")
    print(f"{index} comorbidities added")


def replace_existing_comorbidities_with_refset():
    index = 0
    # ecl = '<< 35919005'
    # comorbidity_choices = fetch_ecl(ecl)
    comorbidity_choices = fetch_paediatric_neurodisability_outpatient_diagnosis_simple_reference_set()
    for comorbidity in ComorbidityEntity.objects.all():
        comorbidity.conceptId = comorbidity_choices[index]['conceptId']
        comorbidity.term = comorbidity_choices[index]['term']
        comorbidity.preferredTerm = comorbidity_choices[index]['preferredTerm']
        comorbidity.save()
        index += 1
    for counter in range(index, len(comorbidity_choices)-1):
        ComorbidityEntity.objects.create(
            conceptId=comorbidity_choices[counter]['conceptId'],
            term=comorbidity_choices[counter]['term'],
            preferredTerm=comorbidity_choices[counter]['preferredTerm'],
            description=None,
            snomed_ct_edition=None,
            snomed_ct_version=None,
            icd_code=None,
            icd_version=None,
            dsm_code=None,
            dsm_version=None,
        )
    print('Update all comorbidites with refset')


def run_medicines_seed():
    for benzo in SNOMED_BENZODIAZEPINE_TYPES:
        concept = fetch_ecl(benzo[0])
        if not MedicineEntity.objects.filter(
                medicine_name=benzo[1]).exists():
            # if the drug is not in the database already
            new_drug = MedicineEntity(
                medicine_name=benzo[1],
                is_rescue=True,
                conceptId=concept[0]['conceptId'],
                term=concept[0]['term'],
                preferredTerm=concept[0]['preferredTerm']
            )
            new_drug.save()
        else:
            print(f"{benzo[1]} exists. Skipping...")
    for aem in SNOMED_ANTIEPILEPSY_MEDICINE_TYPES:
        if not MedicineEntity.objects.filter(
            medicine_name=aem[1],
            is_rescue=False
        ).exists():
            # if the drug is not in the database already
            concept = fetch_ecl(aem[0])
            aem_drug = MedicineEntity(
                medicine_name=aem[1],
                conceptId=concept[0]['conceptId'],
                term=concept[0]['term'],
                preferredTerm=concept[0]['preferredTerm']
            )
            aem_drug.save()
        else:
            print(f"{aem_drug[1]} exists. Skipping...")


def add_existing_medicines_as_foreign_keys():
    for antiepilepsy_medicine in AntiEpilepsyMedicine.objects.all():
        if antiepilepsy_medicine.medicine_entity is None and antiepilepsy_medicine.medicine_name is not None:
            # no relationship exists with MedicineEntity yet and a medicine has been allocated previously
            if MedicineEntity.objects.filter(medicine_name=antiepilepsy_medicine.medicine_name).exists():
                new_medicine = MedicineEntity.objects.filter(
                    medicine_name=antiepilepsy_medicine.medicine_name).first()
                antiepilepsy_medicine.medicine_entity = new_medicine
                print(f'Adding {antiepilepsy_medicine.medicine_name}')
                antiepilepsy_medicine.save()


def update_medicine_entity_with_snomed():
    for benzo in SNOMED_BENZODIAZEPINE_TYPES:
        if MedicineEntity.objects.filter(
                medicine_name=benzo[1]).exists():
            # if the drug is not in the database already
            new_drug = MedicineEntity.objects.filter(
                medicine_name=benzo[1],
            ).first()
            new_drug.is_rescue = True
            if benzo[0] not in [1001, 1002]:
                concept = fetch_ecl(benzo[0])
                new_drug.conceptId = concept[0]['conceptId']
                new_drug.term = concept[0]['term']
                new_drug.preferredTerm = concept[0]['preferredTerm']
            new_drug.save()
        else:
            print(f"{benzo[1]} does not exist. Skipping...")
    for aem in SNOMED_ANTIEPILEPSY_MEDICINE_TYPES:
        if MedicineEntity.objects.filter(
            medicine_name=aem[1],
        ).exists():
            # if the drug is not in the database already
            aem_drug = MedicineEntity.objects.filter(
                medicine_name=aem[1],
            ).first()
            aem_drug.is_rescue = False
            if aem[0] not in [1001, 1002]:
                concept = fetch_ecl(aem[0])
                aem_drug.conceptId = concept[0]['conceptId']
                aem_drug.term = concept[0]['term']
                aem_drug.preferredTerm = concept[0]['preferredTerm']
            aem_drug.save()
        else:
            print(f"{aem_drug[1]} does not exist. Skipping...")


def run_organisations_seed_from_nhs_api():
    """
    Seed function to replace the seed function which populates the Organisation table from JSON.
    This instead uses a list provided by RCPCH E12 time of ODSCodes of all organisations in England
    and Wales that care for children with Epilepsy
    This function iterates through the list of codes, and makes and API call for each to api.nhs.uk
    This requires an API key.
    This returns an object of complex structure - much of which is not needed for E12
    {
        "@odata.context": "https://nhsuksearchproduks.search.windows.net/indexes('syndicationprofiles-2-2-c-prod')/$metadata#docs(*)",
        "value": [
            {
                "@search.score": 11.657321,
                "SearchKey": "X99584",
                "ODSCode": "RAL26",
                "OrganisationName": "Barnet Hospital",
                "OrganisationTypeId": "HOS",
                "OrganisationType": "Hospital",
                "OrganisationStatus": "Visible",
                "SummaryText": null,
                "URL": "https://www.royalfree.nhs.uk/",
                "Address1": "Wellhouse Lane",
                "Address2": null,
                "Address3": null,
                "City": "Barnet",
                "County": "Hertfordshire",
                "Latitude": 51.650726318359375,
                "Longitude": -0.21413777768611908,
                "Postcode": "EN5 3DJ",
                "Geocode": {
                    "type": "Point",
                    "coordinates": [
                        -0.214138,
                        51.6507
                    ],
                    "crs": {
                        "type": "name",
                        "properties": {
                            "name": "EPSG:4326"
                        }
                    }
                },
                "OrganisationSubType": "Independent Sector",
                "OrganisationAliases": [],
                "ParentOrganisation": {
                    "ODSCode": "RAL",
                    "OrganisationName": "Royal Free London NHS Foundation Trust"
                },
                "Services": [
                    {
                        "ServiceName": "Accident and emergency services",
                        "ServiceCode": "SRV0001",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [
                            {
                                "Weekday": "Sunday",
                                "Times": "00:00-23:59",
                                "OpeningTime": "00:00",
                                "ClosingTime": "23:59",
                                "OffsetOpeningTime": 0,
                                "OffsetClosingTime": 1439,
                                "OpeningTimeType": "General",
                                "AdditionalOpeningDate": "",
                                "IsOpen": true
                            },
                            {
                                "Weekday": "Tuesday",
                                "Times": "00:00-23:59",
                                "OpeningTime": "00:00",
                                "ClosingTime": "23:59",
                                "OffsetOpeningTime": 0,
                                "OffsetClosingTime": 1439,
                                "OpeningTimeType": "General",
                                "AdditionalOpeningDate": "",
                                "IsOpen": true
                            },
                            {
                                "Weekday": "Friday",
                                "Times": "00:00-23:59",
                                "OpeningTime": "00:00",
                                "ClosingTime": "23:59",
                                "OffsetOpeningTime": 0,
                                "OffsetClosingTime": 1439,
                                "OpeningTimeType": "General",
                                "AdditionalOpeningDate": "",
                                "IsOpen": true
                            },
                            {
                                "Weekday": "Wednesday",
                                "Times": "00:00-23:59",
                                "OpeningTime": "00:00",
                                "ClosingTime": "23:59",
                                "OffsetOpeningTime": 0,
                                "OffsetClosingTime": 1439,
                                "OpeningTimeType": "General",
                                "AdditionalOpeningDate": "",
                                "IsOpen": true
                            },
                            {
                                "Weekday": "Saturday",
                                "Times": "00:00-23:59",
                                "OpeningTime": "00:00",
                                "ClosingTime": "23:59",
                                "OffsetOpeningTime": 0,
                                "OffsetClosingTime": 1439,
                                "OpeningTimeType": "General",
                                "AdditionalOpeningDate": "",
                                "IsOpen": true
                            },
                            {
                                "Weekday": "Monday",
                                "Times": "00:00-23:59",
                                "OpeningTime": "00:00",
                                "ClosingTime": "23:59",
                                "OffsetOpeningTime": 0,
                                "OffsetClosingTime": 1439,
                                "OpeningTimeType": "General",
                                "AdditionalOpeningDate": "",
                                "IsOpen": true
                            },
                            {
                                "Weekday": "Thursday",
                                "Times": "00:00-23:59",
                                "OpeningTime": "00:00",
                                "ClosingTime": "23:59",
                                "OffsetOpeningTime": 0,
                                "OffsetClosingTime": 1439,
                                "OpeningTimeType": "General",
                                "AdditionalOpeningDate": "",
                                "IsOpen": true
                            },
                            {
                                "Weekday": "",
                                "Times": "00:00-23:59",
                                "OpeningTime": "00:00",
                                "ClosingTime": "23:59",
                                "OffsetOpeningTime": 0,
                                "OffsetClosingTime": 1439,
                                "OpeningTimeType": "Additional",
                                "AdditionalOpeningDate": "Dec 25 2023",
                                "IsOpen": true
                            },
                            {
                                "Weekday": "",
                                "Times": "00:00-23:59",
                                "OpeningTime": "00:00",
                                "ClosingTime": "23:59",
                                "OffsetOpeningTime": 0,
                                "OffsetClosingTime": 1439,
                                "OpeningTimeType": "Additional",
                                "AdditionalOpeningDate": "Aug 28 2023",
                                "IsOpen": true
                            },
                            {
                                "Weekday": "",
                                "Times": "00:00-23:59",
                                "OpeningTime": "00:00",
                                "ClosingTime": "23:59",
                                "OffsetOpeningTime": 0,
                                "OffsetClosingTime": 1439,
                                "OpeningTimeType": "Additional",
                                "AdditionalOpeningDate": "May 29 2023",
                                "IsOpen": true
                            },
                            {
                                "Weekday": "",
                                "Times": "00:00-23:59",
                                "OpeningTime": "00:00",
                                "ClosingTime": "23:59",
                                "OffsetOpeningTime": 0,
                                "OffsetClosingTime": 1439,
                                "OpeningTimeType": "Additional",
                                "AdditionalOpeningDate": "May  8 2023",
                                "IsOpen": true
                            },
                            {
                                "Weekday": "",
                                "Times": "00:00-23:59",
                                "OpeningTime": "00:00",
                                "ClosingTime": "23:59",
                                "OffsetOpeningTime": 0,
                                "OffsetClosingTime": 1439,
                                "OpeningTimeType": "Additional",
                                "AdditionalOpeningDate": "May  1 2023",
                                "IsOpen": true
                            },
                            {
                                "Weekday": "",
                                "Times": "00:00-23:59",
                                "OpeningTime": "00:00",
                                "ClosingTime": "23:59",
                                "OffsetOpeningTime": 0,
                                "OffsetClosingTime": 1439,
                                "OpeningTimeType": "Additional",
                                "AdditionalOpeningDate": "Dec 26 2023",
                                "IsOpen": true
                            }
                        ],
                        "AgeRange": [
                            {
                                "FromAgeDays": 0,
                                "ToAgeDays": 47481
                            }
                        ],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Acute Internal Medicine",
                        "ServiceCode": "SRV0483",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Breast cancer services",
                        "ServiceCode": "SRV0117",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Breast Surgery",
                        "ServiceCode": "SRV0011",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Other symptomatic Breast (2WW)"
                            },
                            {
                                "Name": "Breast cancer family history service"
                            },
                            {
                                "Name": "Oncology Established Diagnosis (non 2WW)"
                            },
                            {
                                "Name": "Mammoplasty (non 2WW)"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Cardiology",
                        "ServiceCode": "SRV0014",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "General Cardiology"
                            },
                            {
                                "Name": "Heart Failure"
                            },
                            {
                                "Name": "Rapid Access Chest Pain inc Exercise ECG"
                            },
                            {
                                "Name": "Lipid Management"
                            },
                            {
                                "Name": "Ischaemic Heart Disease"
                            },
                            {
                                "Name": "Arrhythmia"
                            },
                            {
                                "Name": "Hypertension"
                            },
                            {
                                "Name": "Valve Disorders"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": [
                            {
                                "MetricID": 74,
                                "MetricName": "RTT 92%",
                                "Description": "Weeks within which 92% of patients were treated",
                                "Text": "Up to 27 weeks for 9/10 patients",
                                "LinkText": null,
                                "MetricDisplayTypeID": 5,
                                "BandingClassification": "Exclamation"
                            }
                        ]
                    },
                    {
                        "ServiceName": "Children's & Adolescent Services",
                        "ServiceCode": "SRV0017",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Ophthal - Orthoptics"
                            },
                            {
                                "Name": "Ophthal - Strabismus / Ocular Motility"
                            },
                            {
                                "Name": "General ophthalmology - Child and adolescent"
                            },
                            {
                                "Name": "Rheumatology"
                            },
                            {
                                "Name": "Neurology"
                            },
                            {
                                "Name": "Gynaecology"
                            },
                            {
                                "Name": "Immunology"
                            },
                            {
                                "Name": "Diabetes"
                            },
                            {
                                "Name": "General surgery - Child and adolescent"
                            },
                            {
                                "Name": "Cardiology"
                            },
                            {
                                "Name": "Urology"
                            },
                            {
                                "Name": "Oral and Maxillofacial Surgery"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Chronic Obstructive Pulmonary Disease",
                        "ServiceCode": "SRV0548",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Colorectal cancer services",
                        "ServiceCode": "SRV0127",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Dementia Services",
                        "ServiceCode": "SRV0536",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Dermatology",
                        "ServiceCode": "SRV0028",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "General dermatology"
                            },
                            {
                                "Name": "Connective Tissue Disease"
                            },
                            {
                                "Name": "Eczema and Dermatitis"
                            },
                            {
                                "Name": "Patch Testing for Contact Dermatitis"
                            },
                            {
                                "Name": "Vulval Skin Disorders"
                            },
                            {
                                "Name": "Leg Ulcer"
                            },
                            {
                                "Name": "Male Genital Skin Disorders"
                            },
                            {
                                "Name": "Nails"
                            },
                            {
                                "Name": "Hair"
                            },
                            {
                                "Name": "Psoriasis"
                            },
                            {
                                "Name": "Cosmetic Camouflage"
                            },
                            {
                                "Name": "Acne"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": [
                            {
                                "MetricID": 74,
                                "MetricName": "RTT 92%",
                                "Description": "Weeks within which 92% of patients were treated",
                                "Text": "Up to 45 weeks for 9/10 patients",
                                "LinkText": null,
                                "MetricDisplayTypeID": 5,
                                "BandingClassification": "Exclamation"
                            }
                        ]
                    },
                    {
                        "ServiceName": "Diabetic Medicine",
                        "ServiceCode": "SRV0029",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Renal Diabetes"
                            },
                            {
                                "Name": "General Diabetic Management"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Diagnostic Physiological Measurement",
                        "ServiceCode": "SRV0327",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Audiology - Hearing Assess / Reassess"
                            },
                            {
                                "Name": "Respiratory - Sleep Apnoea Screening"
                            },
                            {
                                "Name": "Cardiac Physiology - Echocardiogram"
                            },
                            {
                                "Name": "Cardiac Physiology - BP Monitoring"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Ear, Nose & Throat",
                        "ServiceCode": "SRV0032",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Ear"
                            },
                            {
                                "Name": "Throat (incl Voice / Swallowing)"
                            },
                            {
                                "Name": "General ENT treatment"
                            },
                            {
                                "Name": "Salivary Gland"
                            },
                            {
                                "Name": "Hospital hearing tests and aids treatment"
                            },
                            {
                                "Name": "Tinnitus"
                            },
                            {
                                "Name": "Balance / Dizziness"
                            },
                            {
                                "Name": "Nose / Sinus"
                            },
                            {
                                "Name": "Facial Plastic and Skin Lesions"
                            },
                            {
                                "Name": "Neck Lump / Thyroid"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": [
                            {
                                "MetricID": 74,
                                "MetricName": "RTT 92%",
                                "Description": "Weeks within which 92% of patients were treated",
                                "Text": "Up to 42 weeks for 9/10 patients",
                                "LinkText": null,
                                "MetricDisplayTypeID": 5,
                                "BandingClassification": "Exclamation"
                            }
                        ]
                    },
                    {
                        "ServiceName": "Emergency Abdominal Surgery",
                        "ServiceCode": "SRV0533",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Endocrinology and Metabolic Medicine",
                        "ServiceCode": "SRV0037",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Pituitary & Hypothalamic"
                            },
                            {
                                "Name": "General endocrinology and metabolic medicine"
                            },
                            {
                                "Name": "Thyroid / Parathyroid"
                            },
                            {
                                "Name": "Gynaecological Endocrinology"
                            },
                            {
                                "Name": "Adrenal Disorders"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Gastrointestinal and Liver services",
                        "ServiceCode": "SRV0042",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Upper GI incl Dyspepsia"
                            },
                            {
                                "Name": "Hepatology"
                            },
                            {
                                "Name": "Colorectal Surgery"
                            },
                            {
                                "Name": "Inflammatory Bowel Disease (IBD)"
                            },
                            {
                                "Name": "Lower GI (medical) excl IBD"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": [
                            {
                                "MetricID": 74,
                                "MetricName": "RTT 92%",
                                "Description": "Weeks within which 92% of patients were treated",
                                "Text": "Up to 39 weeks for 9/10 patients",
                                "LinkText": null,
                                "MetricDisplayTypeID": 5,
                                "BandingClassification": "Exclamation"
                            }
                        ]
                    },
                    {
                        "ServiceName": "General Surgery",
                        "ServiceCode": "SRV0045",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Hernias"
                            },
                            {
                                "Name": "Lumps and Bumps"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": [
                            {
                                "MetricID": 74,
                                "MetricName": "RTT 92%",
                                "Description": "Weeks within which 92% of patients were treated",
                                "Text": "Up to 48 weeks for 9/10 patients",
                                "LinkText": null,
                                "MetricDisplayTypeID": 5,
                                "BandingClassification": "Exclamation"
                            }
                        ]
                    },
                    {
                        "ServiceName": "Geriatric Medicine",
                        "ServiceCode": "SRV0048",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "General geriatric medicine"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": [
                            {
                                "MetricID": 74,
                                "MetricName": "RTT 92%",
                                "Description": "Weeks within which 92% of patients were treated",
                                "Text": "Up to 36 weeks for 9/10 patients",
                                "LinkText": null,
                                "MetricDisplayTypeID": 5,
                                "BandingClassification": "Exclamation"
                            }
                        ]
                    },
                    {
                        "ServiceName": "Gynaecology",
                        "ServiceCode": "SRV0049",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Infertility"
                            },
                            {
                                "Name": "Menopause"
                            },
                            {
                                "Name": "Menstrual Disorders"
                            },
                            {
                                "Name": "Urogynaecology / Prolapse"
                            },
                            {
                                "Name": "Perineal Repair"
                            },
                            {
                                "Name": "Vulval and Perineal Lesions"
                            },
                            {
                                "Name": "General gynaecology"
                            },
                            {
                                "Name": "Recurrent Miscarriage"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": [
                            {
                                "MetricID": 74,
                                "MetricName": "RTT 92%",
                                "Description": "Weeks within which 92% of patients were treated",
                                "Text": "Up to 47 weeks for 9/10 patients",
                                "LinkText": null,
                                "MetricDisplayTypeID": 5,
                                "BandingClassification": "Exclamation"
                            }
                        ]
                    },
                    {
                        "ServiceName": "Haematology",
                        "ServiceCode": "SRV0050",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Clotting Disorders"
                            },
                            {
                                "Name": "General haematology"
                            },
                            {
                                "Name": "Anti Coagulant"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Inpatient Diabetes",
                        "ServiceCode": "SRV0547",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Intensive Care",
                        "ServiceCode": "SRV0534",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Major trauma",
                        "ServiceCode": "SRV0493",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Maternity services",
                        "ServiceCode": "SRV0370",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Neonatal Care",
                        "ServiceCode": "SRV0537",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Nephrology",
                        "ServiceCode": "SRV0091",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Renal Diabetes"
                            },
                            {
                                "Name": "Hypertension"
                            },
                            {
                                "Name": "Nephrology"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Neurology",
                        "ServiceCode": "SRV0064",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Parkinsons / Movement Disorders"
                            },
                            {
                                "Name": "General neurology"
                            },
                            {
                                "Name": "Epilepsy"
                            },
                            {
                                "Name": "Headache and migraine"
                            },
                            {
                                "Name": "Cognitive Disorders"
                            },
                            {
                                "Name": "Neuromuscular"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": [
                            {
                                "MetricID": 74,
                                "MetricName": "RTT 92%",
                                "Description": "Weeks within which 92% of patients were treated",
                                "Text": "Up to 36 weeks for 9/10 patients",
                                "LinkText": null,
                                "MetricDisplayTypeID": 5,
                                "BandingClassification": "Exclamation"
                            }
                        ]
                    },
                    {
                        "ServiceName": "Obstetrics And Gynaecology",
                        "ServiceCode": "SRV0485",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Ophthalmology",
                        "ServiceCode": "SRV0070",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Glaucoma"
                            },
                            {
                                "Name": "Low Vision"
                            },
                            {
                                "Name": "Cataract"
                            },
                            {
                                "Name": "Oculoplastics/Orbits/Lacrimal"
                            },
                            {
                                "Name": "Orthoptics"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": [
                            {
                                "MetricID": 74,
                                "MetricName": "RTT 92%",
                                "Description": "Weeks within which 92% of patients were treated",
                                "Text": "Up to 36 weeks for 9/10 patients",
                                "LinkText": null,
                                "MetricDisplayTypeID": 5,
                                "BandingClassification": "Exclamation"
                            }
                        ]
                    },
                    {
                        "ServiceName": "Oral and Maxillofacial Surgery",
                        "ServiceCode": "SRV0071",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Oncology (Established Diagnosis)"
                            },
                            {
                                "Name": "Salivary Gland Disease"
                            },
                            {
                                "Name": "Head and Neck Lumps (not 2WW)"
                            },
                            {
                                "Name": "Facial Plastics"
                            },
                            {
                                "Name": "Oral Surgery"
                            },
                            {
                                "Name": "Facial Deformity"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": [
                            {
                                "MetricID": 74,
                                "MetricName": "RTT 92%",
                                "Description": "Weeks within which 92% of patients were treated",
                                "Text": "Numbers of patients too low to report a waiting time ",
                                "LinkText": null,
                                "MetricDisplayTypeID": 5,
                                "BandingClassification": "NULL"
                            }
                        ]
                    },
                    {
                        "ServiceName": "Orthopaedics",
                        "ServiceCode": "SRV0073",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Foot and Ankle"
                            },
                            {
                                "Name": "Knee replacement"
                            },
                            {
                                "Name": "Hip Fracture"
                            },
                            {
                                "Name": "Hip replacement"
                            },
                            {
                                "Name": "Hand and Wrist"
                            },
                            {
                                "Name": "Fracture - Non Emergency"
                            },
                            {
                                "Name": "Sports Trauma"
                            },
                            {
                                "Name": "Spine - Neck Pain"
                            },
                            {
                                "Name": "Spine - Back Pain (not Scoliosis/Deform)"
                            },
                            {
                                "Name": "Podiatric Surgery"
                            },
                            {
                                "Name": "Shoulder and Elbow"
                            },
                            {
                                "Name": "Spine - Scoliosis and Deformity"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": [
                            {
                                "MetricID": 74,
                                "MetricName": "RTT 92%",
                                "Description": "Weeks within which 92% of patients were treated",
                                "Text": "Up to 58 weeks for 9/10 patients",
                                "LinkText": null,
                                "MetricDisplayTypeID": 5,
                                "BandingClassification": "Exclamation"
                            }
                        ]
                    },
                    {
                        "ServiceName": "Paediatric Surgery",
                        "ServiceCode": "SRV0544",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Pain Management",
                        "ServiceCode": "SRV0076",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Pain Management"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Physiotherapy",
                        "ServiceCode": "SRV0081",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Musculoskeletal"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Plastic surgery",
                        "ServiceCode": "SRV0082",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Minor Plastic Surgery"
                            },
                            {
                                "Name": "Mammoplasty"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": [
                            {
                                "MetricID": 74,
                                "MetricName": "RTT 92%",
                                "Description": "Weeks within which 92% of patients were treated",
                                "Text": "Up to 54 weeks for 9/10 patients",
                                "LinkText": null,
                                "MetricDisplayTypeID": 5,
                                "BandingClassification": "Exclamation"
                            }
                        ]
                    },
                    {
                        "ServiceName": "Podiatry",
                        "ServiceCode": "SRV0083",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Nail Surgery"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Prostate Cancer Service",
                        "ServiceCode": "SRV0538",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Respiratory Medicine",
                        "ServiceCode": "SRV0092",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "General respiratory medicine"
                            },
                            {
                                "Name": "Occupational Lung Disease"
                            },
                            {
                                "Name": "Asthma"
                            },
                            {
                                "Name": "Interstitial Lung Disease"
                            },
                            {
                                "Name": "COPD"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": [
                            {
                                "MetricID": 74,
                                "MetricName": "RTT 92%",
                                "Description": "Weeks within which 92% of patients were treated",
                                "Text": "Up to 41 weeks for 9/10 patients",
                                "LinkText": null,
                                "MetricDisplayTypeID": 5,
                                "BandingClassification": "Exclamation"
                            }
                        ]
                    },
                    {
                        "ServiceName": "Rheumatology",
                        "ServiceCode": "SRV0093",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Bone / Osteoporosis"
                            },
                            {
                                "Name": "Musculoskeletal"
                            },
                            {
                                "Name": "Inflammatory Arthritis"
                            },
                            {
                                "Name": "Other Autoimmune Rheumatic Disease"
                            },
                            {
                                "Name": "Spinal Disorders"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": [
                            {
                                "MetricID": 74,
                                "MetricName": "RTT 92%",
                                "Description": "Weeks within which 92% of patients were treated",
                                "Text": "Up to 32 weeks for 9/10 patients",
                                "LinkText": null,
                                "MetricDisplayTypeID": 5,
                                "BandingClassification": "Exclamation"
                            }
                        ]
                    },
                    {
                        "ServiceName": "Stroke",
                        "ServiceCode": "SRV0174",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    },
                    {
                        "ServiceName": "Urology",
                        "ServiceCode": "SRV0103",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": [
                            {
                                "MetricID": 74,
                                "MetricName": "RTT 92%",
                                "Description": "Weeks within which 92% of patients were treated",
                                "Text": "Up to 49 weeks for 9/10 patients",
                                "LinkText": null,
                                "MetricDisplayTypeID": 5,
                                "BandingClassification": "Exclamation"
                            }
                        ]
                    },
                    {
                        "ServiceName": "Vascular surgery",
                        "ServiceCode": "SRV0104",
                        "ServiceDescription": null,
                        "Contacts": [],
                        "ServiceProvider": {
                            "ODSCode": "RAL",
                            "OrganisationName": "Royal Free London NHS Foundation Trust"
                        },
                        "Treatments": [
                            {
                                "Name": "Varicose Veins"
                            },
                            {
                                "Name": "Arterial"
                            },
                            {
                                "Name": "Leg Ulcer"
                            },
                            {
                                "Name": "General vascular surgery"
                            }
                        ],
                        "OpeningTimes": [],
                        "AgeRange": [],
                        "Metrics": []
                    }
                ],
                "OpeningTimes": [],
                "Contacts": [
                    {
                        "ContactType": "PALS",
                        "ContactAvailabilityType": "Office hours",
                        "ContactMethodType": "Email",
                        "ContactValue": "bcfpals@nhs.net"
                    },
                    {
                        "ContactType": "Primary",
                        "ContactAvailabilityType": "Office hours",
                        "ContactMethodType": "Telephone",
                        "ContactValue": "020 8216 4600"
                    },
                    {
                        "ContactType": "Primary",
                        "ContactAvailabilityType": "Office hours",
                        "ContactMethodType": "Website",
                        "ContactValue": "https://www.royalfree.nhs.uk/"
                    }
                ],
                "Facilities": [],
                "Staff": [],
                "GSD": null,
                "LastUpdatedDates": {
                    "OpeningTimes": null,
                    "BankHolidayOpeningTimes": null,
                    "DentistsAcceptingPatients": null,
                    "Facilities": "2014-02-26T13:06:12Z",
                    "HospitalDepartment": "2023-04-20T01:37:52.803Z",
                    "Services": "2014-02-26T13:06:12Z",
                    "ContactDetails": "2019-11-26T10:23:16Z",
                    "AcceptingPatients": null
                },
                "AcceptingPatients": {
                    "GP": null,
                    "Dentist": []
                },
                "GPRegistration": null,
                "CCG": null,
                "RelatedIAPTCCGs": [],
                "CCGLocalAuthority": [],
                "Trusts": [],
                "Metrics": [
                    {
                        "MetricID": 8175,
                        "MetricName": "Care Quality Commission inspection ratings shadowed",
                        "DisplayName": "Care Quality Commission inspection ratings",
                        "Description": "Care Quality Commission inspection ratings",
                        "Value": "3",
                        "Value2": null,
                        "Value3": null,
                        "Text": "Requires Improvement",
                        "LinkUrl": "http://www.cqc.org.uk/location/RAL26",
                        "LinkText": "Visit CQC profile",
                        "MetricDisplayTypeID": 5,
                        "MetricDisplayTypeName": "BandingImage",
                        "HospitalSectorType": "Independent Sector",
                        "MetricText": "[BandingName]",
                        "DefaultText": null,
                        "IsMetaMetric": true,
                        "BandingClassification": "cqc-requiresimp",
                        "BandingName": "Requires Improvement"
                    }
                ]
            }
        ]
    }

    Items to persist from this object include:
    {
        "ODSCode": "RAL26",
        "OrganisationName": "Barnet Hospital",
        "OrganisationTypeId": "HOS",
        "OrganisationType": "Hospital",
        "OrganisationStatus": "Visible",
        "SummaryText": null,
        "URL": "https://www.royalfree.nhs.uk/",
        "Address1": "Wellhouse Lane",
        "Address2": null,
        "Address3": null,
        "City": "Barnet",
        "County": "Hertfordshire",
        "Latitude": 51.650726318359375,
        "Longitude": -0.21413777768611908,
        "Postcode": "EN5 3DJ",
        "Geocode": {
            "type": "Point",
            "coordinates": [
                -0.214138,
                51.6507
            ],
            "crs": {
                "type": "name",
                "properties": {
                    "name": "EPSG:4326"
                }
            }
        },
        "OrganisationSubType": "Independent Sector",
        "OrganisationAliases": [],
        "ParentOrganisation": {
            "ODSCode": "RAL",
            "OrganisationName": "Royal Free London NHS Foundation Trust"
        },
    }

    Arguably, if anything more detailed is needed, it could be fetched directly from api.nhs.uk

    The seeding of organisations should happen in a migration but could potentially be run from here on the command line.
    """

    if len(RCPCH_ORGANISATION_CODES) == Organisation.objects.all().count():
        # TODO run a conditional here to identify if this is a more up to date list of organisations and therefor update the database
        print(f"{Organisation.objects.all().count()} Organisations already exist in the database. Skipping seeding...")
        return
    else:
        # The database needs seeding
        for rcpch_organisation_ods_code in RCPCH_ORGANISATION_CODES:
            try:
                new_organisation = fetch_ods(rcpch_organisation_ods_code)
            except:
                print(
                    f"{rcpch_organisation_ods_code} does not match any codes in api.nhs.uk")
                return

            organisation = Organisation.objects.create(
                ODSCode=new_organisation["ODSCode"],
                OrganisationName=new_organisation["OrganisationName"],
                OrganisationTypeId=new_organisation["OrganisationTypeId"],
                OrganisationType=new_organisation["OrganisationType"],
                OrganisationStatus=new_organisation["OrganisationStatus"],
                SummaryText=new_organisation["SummaryText"],
                URL=new_organisation["URL"],
                Address1=new_organisation["Address1"],
                Address2=new_organisation["Address2"],
                Address3=new_organisation["Address3"],
                City=new_organisation["City"],
                County=new_organisation["County"],
                Latitude=new_organisation["Latitude"],
                Longitude=new_organisation["Longitude"],
                Postcode=new_organisation["Postcode"],
                Geocode=new_organisation["Geocode"],
                OrganisationSubType=new_organisation["OrganisationSubType"],
                OrganisationAliases=new_organisation["OrganisationAliases"],
                ParentOrganisation=new_organisation["ParentOrganisation"],

            )


def run_organisations_seed():
    # this adds all the English organisations from JSON in the constants folder
    # There are also lists of organisations across northern ireland, wales and scotland, but the JSON has a different structure
    if Organisation.objects.all().exists():
        print('Organisation table already exists. Skipping this step...')
        return
    added = 0
    for index, organisation in enumerate(ALL_HOSPITALS):
        if organisation["Sector"] == "NHS Sector":
            organisation = Organisation(
                OrganisationID=organisation.get("OrganisationID"),
                OrganisationCode=organisation.get("OrganisationCode", None),
                OrganisationType=organisation.get("OrganisationType", None),
                SubType=organisation.get("SubType", None),
                Sector=organisation.get("Sector", None),
                OrganisationStatus=organisation.get(
                    "OrganisationStatus", None),
                IsPimsManaged=organisation.get("IsPimsManaged", None),
                OrganisationName=organisation.get("OrganisationName", None),
                Address1=organisation.get("Address1", None),
                Address2=organisation.get("Address2", None),
                Address3=organisation.get("Address3", None),
                City=organisation.get("City", None),
                County=organisation.get("County", None),
                Postcode=organisation.get("Postcode", None),
                Latitude=organisation.get("Latitude", None),
                Longitude=organisation.get("Longitude", None),
                ParentODSCode=organisation.get("ParentODSCode", None),
                ParentName=organisation.get("ParentName", None),
                Phone=organisation.get("Phone", None),
                Email=organisation.get("Email", None),
                Website=organisation.get("Website", None),
                Fax=organisation.get("Fax", None),
                DateValid=date(2023, 1, 1)
            )

            add_codes_to_organisation(organisation=organisation)

            try:
                organisation.save()
            except Exception as error:
                print("Exception at "+organisation.ParentName)
                print(error)
            added += 1
            chosen_organisation = organisation.OrganisationName
            print(
                '\033[31m', f"New English organisation added...{added}: {chosen_organisation}", '\033[31m')
    print(f"English organisations added...{added}")

    run_welsh_organisations_seed()


def run_welsh_organisations_seed():
    # this adds all the English organisations from JSON in the constants folder
    # There are also lists of organisations across northern ireland, wales and scotland, but the JSON has a different structure
    added = 0

    for index, organisation in enumerate(WELSH_HOSPITALS):
        try:
            welsh_organisation = Organisation(
                OrganisationID=index + 90000,
                OrganisationCode=organisation.get(
                    "OrganisationCode", None),
                OrganisationType=organisation.get("OrganisationType", None),
                SubType=organisation.get("SubType", None),
                Sector=organisation.get("Sector", None),
                OrganisationStatus=organisation.get(
                    "OrganisationStatus", None),
                IsPimsManaged=organisation.get("IsPimsManaged", None),
                OrganisationName=organisation.get("OrganisationName", None),
                Address1=organisation.get("Address1", None),
                Address2=organisation.get("Address2", None),
                Address3=organisation.get("Address3", None),
                City=organisation.get("City", None),
                County=organisation.get("County", None),
                Postcode=organisation.get("Postcode", None),
                Latitude=organisation.get("Latitude", None),
                Longitude=organisation.get("Longitude", None),
                ParentODSCode=organisation.get("ParentODSCode", None),
                ParentName=organisation.get("ParentName", None),
                Phone=organisation.get("Phone", None),
                Email=organisation.get("Email", None),
                Website=organisation.get("Website", None),
                Fax=organisation.get("Fax", None),
                DateValid=date(2023, 1, 1)
            )
            welsh_organisation.save()
            print(
                '\033[94m', f"New Welsh organisation added...{added}: {welsh_organisation.OrganisationName}({welsh_organisation.ParentName})", '\033[94m')
            added += 1

            add_codes_to_organisation(welsh_organisation)

        except Exception as error:
            print("Exception creating "+organisation["OrganisationName"])

    print(f"Welsh organisations added...{added}")


def add_codes_to_english_organisations():
    """
    A custom function to run in the rare likelihood that an existing table of organisations exists but does not have 
    the ODS codes in it
    """
    index = 0
    for organisation in Organisation.objects.all():
        add_codes_to_organisation(organisation)
        index += 1
    print(f'Updated {index} English organisations with ODS Codes.')


def delete_organisations():
    try:
        Organisation.objects.all().delete()
    except:
        print("Unable to delete Organisation table")
    print("...all organisations deleted.")


def run_dummy_cases_seed():
    added = 0

    # there should not be any cases yet, but sometimes seed gets run more than once
    if Case.objects.all().exists():
        print(f'Cases already exist. Skipping this step...')
        return

    postcode_list = random_postcodes.generate_postcodes(requested_number=100)

    random_organisations = []

    # first populate 1b St Catherines Way Gorleston for ease of dev testing
    for _ in range(1, 11):
        random_organisations.append(
            Organisation.objects.get(OrganisationID='3775035'))

    # seed the remaining 9
    for j in range(9):
        random_organisation = Organisation.objects.filter(
            Sector="NHS Sector").order_by("?").first()
        for i in range(1, 11):
            random_organisations.append(random_organisation)

    for index in range(len(DUMMY_NAMES)-1):
        random_date = date(randint(2005, 2021), randint(1, 12), randint(1, 28))
        nhs_number = randint(1000000000, 9999999999)
        first_name = DUMMY_NAMES[index]['firstname']
        surname = DUMMY_NAMES[index]['lastname']
        gender_object = DUMMY_NAMES[index]['gender']
        if gender_object == 'm':
            sex = 1
        else:
            sex = 2
        date_of_birth = random_date
        postcode = postcode_list[index]
        ethnicity = choice(ETHNICITIES)[0]

        # get a random organisation
        organisation = random_organisations[index]

        case_has_error = False

        try:
            new_case = Case(
                locked=False,
                nhs_number=nhs_number,
                first_name=first_name,
                surname=surname,
                sex=sex,
                date_of_birth=date_of_birth,
                postcode=postcode,
                ethnicity=ethnicity
            )
            new_case.save()
        except Exception as e:
            print(f"Error saving case: {e}")
            case_has_error = True

        if not case_has_error:
            try:
                new_site = Site.objects.create(
                    organisation=organisation,
                    site_is_actively_involved_in_epilepsy_care=True,
                    site_is_primary_centre_of_epilepsy_care=True,
                    case=new_case
                )
                new_site.save()
            except Exception as e:
                print(f"Error saving site: {e}")

            added += 1
            print(
                f"Saved {new_case.first_name} {new_case.surname} at {new_site.organisation.ParentName}({new_site.organisation.OrganisationName})...")
    print(f"Saved {added} cases.")


def run_registrations():
    """
    Calling function to register all cases in Epilepsy12 and complete all fields with random answers
    """
    create_registrations()

    complete_registrations()


def complete_registrations():
    """
    Loop through the registrations and score all fields
    """
    for registration in Registration.objects.all():
        current_cohort_end_date = first_tuesday_in_january(
            current_cohort_start_date().year + 2) + relativedelta(days=7)
        registration.registration_date = random_date(
            start=current_cohort_start_date(), end=current_cohort_end_date)
        registration.eligibility_criteria_met = True
        registration.save()

        create_epilepsy12_record(registration_instance=registration)

    # calculate national level kpis
    # kpis_for_abstraction_level()


def image():
    return """

                                .^~^      ^777777!~:       ^!???7~:
                                ^JJJ:.:!^ 7#BGPPPGBGY:   !5BBGPPGBBY.
                                 :~!!?J~. !BBJ    YBB?  ?BB5~.  .~J^
                              .:~7?JJ?:   !BBY^~~!PBB~ .GBG:
                              .~!?JJJJ^   !BBGGGBBBY^  .PBG^
                                 ?J~~7?:  !BBJ.:?BB5^   ~GBG?^:^~JP7
                                :?:   .   !BBJ   ~PBG?.  :?PBBBBBG5!
                                ..::...     .::. ...:^::. .. .:^~~^:.
                                !GPGGGGPY7.   :!?JJJJ?7~..PGP:    !GGJ
                                7BBY~~!YBBY  !JJ?!^^^!??::GBG:    7BBJ
                                7BB?   .GBG.^JJ7.     .. .GBG!^^^^JBBJ
                                7BB577?5BBJ ~JJ!         .GBBGGGGGGBBJ
                                7BBGPPP5J~  :JJJ^.   .^^ .GBG^.::.?BBJ
                                7#B?         :7JJ?77?JJ?^:GBB:    7##Y
                                ~YY!           :~!77!!^. .JYJ.    ~YY7


                                           Epilepsy12 2022

                """
