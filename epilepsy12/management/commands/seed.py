from logging import exception
from unicodedata import name
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from random import randint, getrandbits, choice
from datetime import date
from django.core.management.base import BaseCommand
from epilepsy12.constants.ethnicities import ETHNICITIES

from epilepsy12.constants.names import DUMMY_NAMES
from epilepsy12.constants.user_types import EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS, EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS, EPILEPSY12_AUDIT_TEAM_VIEW_ONLY, EPILEPSY12_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS, PATIENT_ACCESS, PATIENT_ACCESS_PERMISSIONS, PERMISSIONS, TRUST_AUDIT_TEAM_EDIT_ACCESS, TRUST_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS, TRUST_AUDIT_TEAM_FULL_ACCESS, TRUST_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS, TRUST_AUDIT_TEAM_VIEW_ONLY, TRUST_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS
from ...models import HospitalTrust, Keyword, Case
from ...constants import ALL_HOSPITALS, KEYWORDS, SEX_TYPE, ROLES
from ...general_functions import random_postcodes


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
            run_dummy_groups_permissions_seed()
        else:
            self.stdout.write('No options supplied...')
        self.stdout.write(image())
        self.stdout.write('done.')


def run_semiology_keywords_seed():
    added = 0
    for index, semiology_keyword in enumerate(KEYWORDS):
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
    postcode_list = random_postcodes.generate_postcodes(requested_number=51)
    for index in range(len(DUMMY_NAMES)):
        random_date = date(randint(2005, 2021), randint(1, 12), randint(1, 28))
        locked = bool(getrandbits(1))
        nhs_number = randint(1000000000, 9999999999)
        first_name = DUMMY_NAMES[index]['name']['firstname']['name']
        surname = DUMMY_NAMES[index]['name']['lastname']['name']
        gender = next(iter([x[0] for x in SEX_TYPE if DUMMY_NAMES[index]
                      ['name']['firstname']['gender_formatted'].capitalize() in x]), None)
        date_of_birth = random_date
        postcode = postcode_list[index]
        ethnicity = choice(ETHNICITIES)[0]

        try:
            new_case = Case(
                locked=locked,
                nhs_number=nhs_number,
                first_name=first_name,
                surname=surname,
                gender=gender,
                date_of_birth=date_of_birth,
                postcode=postcode,
                ethnicity=ethnicity
            )
            new_case.save()
        except Exception as e:
            print(f"Error: {e}")

        added += 1
        print(f"Saved {first_name} {surname}...")
    print(f"Saved {added} cases.")


def run_dummy_groups_permissions_seed():
    group_names = (

    )

    # allocate permissions
    # inspiration from this 'my fish is bigger than yours' post: https://stackoverflow.com/questions/22250352/programmatically-create-a-django-group-with-permissions
    for group in group_names:
        print(f'Creating group: {group}')
        new_group, created = Group.objects.update_or_create(name=group)
        if group == EPILEPSY12_AUDIT_TEAM_VIEW_ONLY:
            # logged in user can view all national data but not logs
            case_ct = ContentType.objects.get_for_model(Case)

            for permission in EPILEPSY12_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS:
                print(f'Adding permission: {permission[1]}')
                permission = Permission.objects.create(
                    codename=permission[0],
                    name=permission[1],
                    content_type=case_ct
                )
                new_group.permissions.add(permission)

        elif group == EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS:
            # logged in user can edit but not delete national data. Cannot view or edit logs or permissions.
            for permission in EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS:
                print(f'Adding permission: {permission[1]}')
                permission = Permission.objects.create(
                    codename=permission[0],
                    name=permission[1],
                    content_type=case_ct
                )
                new_group.permissions.add(permission)

        elif group == TRUST_AUDIT_TEAM_VIEW_ONLY:
            # logged in user can view all data relating to their trust(s) but not logs
            for permission in TRUST_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS:
                print(f'Adding permission: {permission[1]}')
                permission = Permission.objects.create(
                    codename=permission[0],
                    name=permission[1],
                    content_type=case_ct
                )
                new_group.permissions.add(permission)

        elif group == TRUST_AUDIT_TEAM_EDIT_ACCESS:
            # logged in user can edit but not delete all data relating to their trust(s) but not view or edit logs, epilepsy key words and hospital trusts, groups and permissions
            for permission in TRUST_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS:
                print(f'Adding permission: {permission[1]}')
                permission = Permission.objects.create(
                    codename=permission[0],
                    name=permission[1],
                    content_type=case_ct
                )
                new_group.permissions.add(permission)

        elif group == TRUST_AUDIT_TEAM_FULL_ACCESS:
            # logged in user can delete all data relating to their trust(s) but not view or edit logs, epilepsy key words and hospital trusts, groups and permissions
            for permission in TRUST_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS:
                print(f'Adding permission: {permission[1]}')
                permission = Permission.objects.create(
                    codename=permission[0],
                    name=permission[1],
                    content_type=case_ct
                )
                new_group.permissions.add(permission)

        elif group == PATIENT_ACCESS:
            # logged in user can view their own audit data, consent to participation and remove that consent/opt out. Opting out would delete all data relating to them, except the epilepsy12 unique identifier
            for permission in PATIENT_ACCESS_PERMISSIONS:
                print(f'Adding permission: {permission[1]}')
                permission = Permission.objects.create(
                    codename=permission[0],
                    name=permission[1],
                    content_type=case_ct
                )
                new_group.permissions.add(permission)
        else:
            # some kind of error
            raise NameError('Error: Group does not exist')


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


    @@@@@@@@ @@@@@@@@%  *@@@@ @@@@@   .@@@@@@@% @@@@@@@@%   -@@@@@@@. *@@@%  @@@@=    :::   .::::::.   
    @@@@@@@@ @@@@@@@@@% *@@@@ @@@@@   .@@@@@@@% @@@@@@@@@@ :@@@@@@@@@  @@@@  @@@@.  .::::  .::::::::.  
    @@@@@@@@ @@@@@@@@@@:+@@@@ @@@@@   .@@@@@@@% @@@@@@@@@@-%@@@%-@@@@- %@@@: @@@# .::::::  ::::::::::  
    @@@@%=== @@@@+ +@@@**@@@@ @@@@@   .@@@@%=+= @@@@* %@@@+%@@@# @@@@+ :@@@=.@@@=::::::::  ::::. ::::. 
    @@@@#    @@@@+ =@@@**@@@@ @@@@@   .@@@@%    @@@@* *@@@+%@@@# @@@@*  @@@**@@@ ......::  ..:: ..:.:  
    @@@@*    @@@@+ +@@@**@@@@ @@@@@   .@@@@%    @@@@* *@@@+%@@@@:       %@@@%@@@    :....  .... :.:..  
    @@@@#--: @@@@+ +@@@**@@@@ @@@@@   .@@@@%--- @@@@* #@@@+=@@@@@#      +@@@@@@*    .....       .....  
    @@@@@@@# @@@@@@@@@@-+@@@@ @@@@@   .@@@@@@@% @@@@@@%@@@= @@@@@@@-    :@@@@@@     .....      ......  
    @@@@@@@# @@@@@@@@@@ +@@@@ @@@@@   .@@@@@@@% @@@@@@@@@@  .%@@@@@@+    @@@@@@     .....      .....   
    @@@@@@@# @@@@@@@@@: +@@@@ @@@@@   .@@@@@@@% @@@@@@@@@     *@@@@@@    %@@@@@     .....     .....    
    @@@@*    @@@@*.     +@@@@ @@@@@   .@@@@#    @@@@*.         .%@@@@+   #@@@@*     .....    ......    
    @@@@*    @@@@+      +@@@@ @@@@@   .@@@@#    @@@@*      @@@@# @@@@#   -@@@@-     .....    .....     
    @@@@*    @@@@+      +@@@@ @@@@@   .@@@@#    @@@@*      @@@@* @@@@@    @@@@:     .....   .....      
    @@@@*    @@@@+      +@@@@ @@@@@   .@@@@%    @@@@*      %@@@# @@@@@    @@@@.     .....   .....       
    @@@@@@@@ @@@@+      +@@@@ @@@@@@@@.@@@@@@@@ @@@@*      %@@@%:@@@@#    @@@@.     .....  ..........            
    @@@@@@@@ @@@@+      +@@@@ @@@@@@@@.@@@@@@@@ @@@@*      +@@@@@@@@@-    @@@@.     .....  ..........
    @@@@@@@@ @@@@+      +@@@@ @@@@@@@@.@@@@@@@@ @@@@*       #@@@@@@@+     @@@@.     .....  ..........                        

                """
