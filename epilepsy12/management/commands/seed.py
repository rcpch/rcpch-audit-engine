from random import randint, getrandbits, choice
from datetime import date
from django.core.management.base import BaseCommand


from ...constants import ETHNICITIES, DUMMY_NAMES
from ...models import HospitalTrust, Keyword, Case, Site
from ...constants import ALL_HOSPITALS, KEYWORDS
from ...general_functions import random_postcodes
from .create_groups import create_groups, add_permissions_to_existing_groups, delete_and_reallocate_permissions


class Command(BaseCommand):
    help = "seed database with hospital trust data for testing and development."

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help="Mode")

    def handle(self, *args, **options):
        if (options['mode'] == 'delete_hospitals'):
            self.stdout.write('Deleting hospital trust data...')
            delete_hospitals()
        elif (options['mode'] == 'seed_hospitals'):
            self.stdout.write('seeding hospital trust data...')
            run_hospitals_seed()
        elif (options['mode'] == 'seed_semiology_keywords'):
            self.stdout.write('seeding hospital trust data...')
            run_semiology_keywords_seed()
        elif (options['mode'] == 'seed_dummy_cases'):
            self.stdout.write('seeding with dummy case data...')
            run_dummy_cases_seed()
        elif (options['mode'] == 'seed_groups_and_permissions'):
            self.stdout.write('setting up groups and permissions...')
            create_groups()
        elif (options['mode'] == 'add_permissions_to_existing_groups'):
            self.stdout.write('adding permissions to groups...')
            add_permissions_to_existing_groups()
        elif (options['mode'] == 'delete_all_groups_and_recreate'):
            self.stdout.write(
                'deleting all groups/permissions and reallocating...')
            delete_and_reallocate_permissions()

        else:
            self.stdout.write('No options supplied...')
        self.stdout.write(image())
        self.stdout.write('done.')


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


def run_hospitals_seed():
    # this adds all the English hospitals from JSON in the constants folder
    # There are also lists of hospitals across northern ireland, wales and scotland, but the JSON has a different structure
    if HospitalTrust.objects.all().exists():
        print('Hospital table already exists. Skipping this step...')
        return
    added = 0
    for index, hospital in enumerate(ALL_HOSPITALS):
        if hospital["Sector"] == "NHS Sector":
            hospital_trust = HospitalTrust(
                OrganisationID=hospital["OrganisationID"],
                OrganisationCode=hospital["OrganisationCode"],
                OrganisationType=hospital["OrganisationType"],
                SubType=hospital["SubType"],
                Sector=hospital["Sector"],
                OrganisationStatus=hospital["OrganisationStatus"],
                IsPimsManaged=hospital["IsPimsManaged"],
                OrganisationName=hospital["OrganisationName"],
                Address1=hospital["Address1"],
                Address2=hospital["Address2"],
                Address3=hospital["Address3"],
                City=hospital["City"],
                County=hospital["County"],
                Postcode=hospital["Postcode"],
                Latitude=hospital["Latitude"],
                Longitude=hospital["Longitude"],
                ParentODSCode=hospital["ParentODSCode"],
                ParentName=hospital["ParentName"],
                Phone=hospital["Phone"],
                Email=hospital["Email"],
                Website=hospital["Website"],
                Fax=hospital["Fax"]
            )

            try:
                hospital_trust.save()
            except Exception as error:
                print("Exception at "+hospital["ParentName"])
                print(error)
            added += 1
            chosen_hospital = hospital["OrganisationName"]
            print(f"New hospital added...{added}: {chosen_hospital}")
    print(f"Hospitals added...{added}")


def delete_hospitals():
    try:
        HospitalTrust.objects.all().delete()
    except:
        print("Unable to delete Hospital table")
    print("...all hospitals deleted.")


def run_dummy_cases_seed():
    added = 0

    # there should not be any cases yet, but sometimes seed gets run more than once
    if Case.objects.all().exists():
        print(f'Cases already exist. Skipping this step...')
        return

    postcode_list = random_postcodes.generate_postcodes(requested_number=100)

    for index in range(len(DUMMY_NAMES)-1):
        random_date = date(randint(2005, 2021), randint(1, 12), randint(1, 28))
        locked = bool(getrandbits(1))
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

        if index < 33:
            hospital_trust = HospitalTrust.objects.filter(
                OrganisationName="King's College Hospital").get()
        elif index >= 33 and index < 66:
            hospital_trust = HospitalTrust.objects.filter(
                OrganisationName="Addenbrooke's").get()
        else:
            hospital_trust = HospitalTrust.objects.filter(
                OrganisationName='Great North Childrens Hospital').get()

        try:
            new_case = Case(
                locked=locked,
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

        try:
            new_site = Site.objects.create(
                hospital_trust=hospital_trust,
                site_is_actively_involved_in_epilepsy_care=True,
                site_is_primary_centre_of_epilepsy_care=True,
                case=new_case
            )
            new_site.save()
        except Exception as e:
            print(f"Error saving site: {e}")

        added += 1
        print(f"Saved {new_case.first_name} {new_case.surname} at {new_site.hospital_trust.ParentName}({new_site.hospital_trust.OrganisationName})...")
    print(f"Saved {added} cases.")


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
