# python
from operator import itemgetter
from random import randint, choice
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from random import randint
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point


from ...constants import ETHNICITIES, DUMMY_NAMES, SYNDROMES, SNOMED_BENZODIAZEPINE_TYPES, SNOMED_ANTIEPILEPSY_MEDICINE_TYPES, OPEN_UK_NETWORKS, RCPCH_ORGANISATIONS
from ...models import Organisation, Keyword, Case, Site, Registration, SyndromeEntity, EpilepsyCauseEntity, ComorbidityEntity, MedicineEntity, AntiEpilepsyMedicine, IntegratedCareBoardEntity, OPENUKNetworkEntity, NHSRegionEntity, ONSRegionEntity, ONSCountryEntity
from ...constants import ALL_HOSPITALS, KEYWORDS, WELSH_HOSPITALS, INTEGRATED_CARE_BOARDS_LOCAL_AUTHORITIES, WELSH_REGIONS, COUNTRY_CODES, UK_ONS_REGIONS
from ...general_functions import random_postcodes, random_date, first_tuesday_in_january, current_cohort_start_date, fetch_ecl, fetch_paediatric_neurodisability_outpatient_diagnosis_simple_reference_set, ons_region_for_postcode
from .create_groups import create_groups, add_permissions_to_existing_groups, delete_and_reallocate_permissions
from .create_e12_records import create_epilepsy12_record, create_registrations


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
        # elif (options['mode'] == 'replace_comorbidities_with_refset'):
        #     self.stdout.write(
        #         'replacing comorbidites with refset...')
        #     replace_existing_comorbidities_with_refset()
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
    print('\033[33m', 'Seeding all the syndromes...', '\033[33m')
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
    print('\033[33m', 'Seeding all the epilepsy semiology keywords...', '\033[33m')
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
    print('\033[33m', 'Seeding all the epilepsy causes from SNOMED...', '\033[33m')
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
    print('\033[33m', 'Seeding comorbidities from paediatric neurodisability reference set...', '\033[33m')
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


def run_medicines_seed():
    print('\033[33m', 'Seeding all the medicines from SNOMED and local Epilepsy12 list...', '\033[33m')
    for benzo in SNOMED_BENZODIAZEPINE_TYPES:
        if not MedicineEntity.objects.filter(
                medicine_name=benzo[1]).exists():
            # if the drug is not in the database already
            if benzo[0] not in [1001, 1002]:
                concept = fetch_ecl(benzo[0])
                new_drug = MedicineEntity(
                    medicine_name=benzo[1],
                    is_rescue=True,
                    conceptId=concept[0]['conceptId'],
                    term=concept[0]['term'],
                    preferredTerm=concept[0]['preferredTerm']
                )
                new_drug.save()
            else:
                # these are for options other or unknow
                new_drug = MedicineEntity(
                    medicine_name=benzo[1],
                    is_rescue=True,
                    conceptId=None,
                    term=None,
                    preferredTerm=None
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
            if aem[0] not in [1001, 1002]:
                concept = fetch_ecl(aem[0])
                aem_drug = MedicineEntity(
                    is_rescue=False,
                    medicine_name=aem[1],
                    conceptId=concept[0]['conceptId'],
                    term=concept[0]['term'],
                    preferredTerm=concept[0]['preferredTerm']
                )
                aem_drug.save()
            else:
                aem_drug = MedicineEntity(
                    medicine_name=aem[1],
                    conceptId=None,
                    term=None,
                    preferredTerm=None,
                    is_rescue=False
                )
                aem_drug.save()
        else:
            print(f"{aem_drug[1]} exists. Skipping...")
    print('All medicines added.')


def update_medicine_entity_with_snomed():
    """
    Deprecating
    Updates any existing medicines with local list and SNOMED
    """
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


def run_organisations_seed():
    """
    Seed function to replace the seed function which populates the Organisation table from JSON.
    This instead uses a list provided by RCPCH E12 team of all organisations in England
    and Wales that care for children with Epilepsy
    """

    if len(RCPCH_ORGANISATIONS) == Organisation.objects.all().count():
        # TODO run a conditional here to identify if this is a more up to date list of organisations and therefor update the database
        print(f"{Organisation.objects.all().count()} Organisations already exist in the database. Skipping seeding...")
        return
    else:
        # The database needs seeding
        print('\033[31m', "Adding new organisations...", '\033[31m')
        for added, rcpch_organisation in enumerate(RCPCH_ORGANISATIONS):

            # get openuk network code from ods code in constants list
            # this gets openuk network object from table
            open_uk_code = next(
                item for item in OPEN_UK_NETWORKS if item["ods trust code"] == rcpch_organisation["ParentODSCode"])
            open_uk_network = OPENUKNetworkEntity.objects.get(
                OPEN_UK_Network_Code=open_uk_code["OPEN UK Network Code"])

            if open_uk_code['country'] == 'England':
                # get icb from icb list in constants
                # then get icb object from table
                icb_code = next(
                    item for item in INTEGRATED_CARE_BOARDS_LOCAL_AUTHORITIES if item["ODS Trust Code"] == rcpch_organisation["ParentODSCode"])
                integrated_care_board = IntegratedCareBoardEntity.objects.get(
                    ODS_ICB_Code=icb_code["ODS ICB Code"])

                # get nhs england region from icb list in constants
                # then get NHSRegion object from table
                nhs_region = NHSRegionEntity.objects.get(
                    NHS_Region_Code=icb_code["NHS England Region Code"]
                )

                if rcpch_organisation['ParentODSCode'] == "RXP":
                    # postcodes io error - postcodes not found: hacky work around
                    ons_region_name = "North East"
                elif rcpch_organisation['ParentODSCode'] == "RN3":
                    ons_region_name = "South West"
                elif rcpch_organisation['ParentODSCode'] == "RM3":
                    ons_region_name = "North West"
                else:
                    ons_region_name = ons_region_for_postcode(
                        rcpch_organisation['Postcode'])
                ons_region = ONSRegionEntity.objects.filter(
                    Region_ONS_Name=ons_region_name).get()

            elif open_uk_code['country'] == 'Wales':
                #
                health_board = next(
                    item for item in WELSH_REGIONS if item['ODS_Code'] == rcpch_organisation["ParentODSCode"]
                )
                integrated_care_board = None
                nhs_region = NHSRegionEntity.objects.get(
                    NHS_Region_Code=health_board["ODS_Code"])
                ons_region = ONSRegionEntity.objects.filter(
                    Region_ONS_Name="Wales").get()

            else:
                raise Exception(
                    f"{open_uk_code['ods trust code']} is not allocated to a country.")

            if hasattr(rcpch_organisation, "longitude") and hasattr(rcpch_organisation, 'latitude'):
                if len(rcpch_organisation["longitude"]) > 0 and len(rcpch_organisation['latitude']) > 1:
                    latitude = rcpch_organisation['latitude']
                    longitude = rcpch_organisation['longitude']
                    new_point = Point(
                        x=rcpch_organisation["longitude"], y=rcpch_organisation['latitude'])
                else:
                    latitude = None
                    longitude = None
                    new_point = None
            else:
                latitude = None
                longitude = None
                new_point = None

            update_date = datetime(year=2023, month=4, day=19)
            timezone_aware_update_date = timezone.make_aware(
                update_date, timezone.utc)

            try:
                Organisation.objects.create(
                    ODSCode=rcpch_organisation['OrganisationCode'],
                    OrganisationName=rcpch_organisation['OrganisationName'],
                    Website=rcpch_organisation['Website'],
                    Address1=rcpch_organisation['Address1'],
                    Address2=rcpch_organisation['Address2'],
                    Address3=rcpch_organisation['Address3'],
                    City=rcpch_organisation['City'],
                    County=rcpch_organisation['County'],
                    Latitude=latitude,
                    Longitude=longitude,
                    Postcode=rcpch_organisation['Postcode'],
                    Geocode_Coordinates=new_point,
                    ParentOrganisation_ODSCode=rcpch_organisation['ParentODSCode'],
                    ParentOrganisation_OrganisationName=rcpch_organisation['ParentName'],
                    LastUpdatedDate=timezone_aware_update_date,
                    openuk_network=open_uk_network,
                    integrated_care_board=integrated_care_board,
                    nhs_region=nhs_region,
                    ons_region=ons_region
                ).save()
                print(
                    f"{added+1}: {rcpch_organisation['OrganisationName']}")
            except Exception as error:
                print(
                    f"Unable to save {rcpch_organisation['OrganisationName']}: {error}")
    print('All organisations added.')


def delete_organisations():
    try:
        Organisation.objects.all().delete()
    except:
        print("Unable to delete Organisation table")
    print("...all organisations deleted.")


def run_dummy_cases_seed():
    added = 0
    print('\033[33m', 'Seeding fictional cases...', '\033[33m')
    # there should not be any cases yet, but sometimes seed gets run more than once
    if Case.objects.all().exists():
        print(f'Cases already exist. Skipping this step...')
        return

    postcode_list = random_postcodes.generate_postcodes(requested_number=100)

    random_organisations = []

    # first populate Addenbrooke's for ease of dev testing
    for _ in range(1, 11):
        random_organisations.append(
            Organisation.objects.get(ODSCode='RGT01'))

    # seed the remaining 9
    for j in range(9):
        random_organisation = Organisation.objects.order_by("?").first()
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
                f"{new_case.first_name} {new_case.surname} at {new_site.organisation.OrganisationName} ({new_site.organisation.ParentOrganisation_OrganisationName})...")
    print(f"Saved {added} cases.")


def run_registrations():
    """
    Calling function to register all cases in Epilepsy12 and complete all fields with random answers
    """
    print('\033[33m', 'Registering fictional cases in Epilepsy12...', '\033[33m')

    create_registrations()

    complete_registrations()


def complete_registrations():
    """
    Loop through the registrations and score all fields
    """
    print('\033[33m', 'Completing all the Epilepsy12 fields for the fictional cases...', '\033[33m')
    for registration in Registration.objects.all():
        current_cohort_end_date = first_tuesday_in_january(
            current_cohort_start_date().year + 2) + relativedelta(days=7)
        registration.registration_date = random_date(
            start=current_cohort_start_date(), end=current_cohort_end_date)
        registration.eligibility_criteria_met = True
        registration.save()

        create_epilepsy12_record(registration_instance=registration)


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
