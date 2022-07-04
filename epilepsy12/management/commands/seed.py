import math
from random import randint, getrandbits, choice
from datetime import date
from unicodedata import name
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from epilepsy12.constants.ethnicities import ETHNICITIES

from epilepsy12.constants.names import DUMMY_NAMES
from epilepsy12.constants.user_types import GROUPS, Epilepsy12UserGroup
from epilepsy12.models import epilepsy12user
from ...models import HospitalTrust, Keyword, Case
from ...constants import ALL_HOSPITALS, KEYWORDS, SEX_TYPE
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
        elif (options['mode'] == 'create_groups'):
            self.stdout.write('creating groups and allocating permissions...')
            for group in GROUPS:
                run_create_group(group)
        elif (options['mode'] == 'seed_semiology_keywords'):
            self.stdout.write('seeding hospital trust data...')
            run_semiology_keywords_seed()
        elif (options['mode'] == 'seed_dummy_cases'):
            self.stdout.write('seeding with dummy case data...')
            run_dummy_cases_seed()
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


def run_create_group(group_name: str):
    """
    Create group
    Accepts name as a parameter
    """
    Group.objects.get_or_create(name=group_name)
    group = Group.objects.get(name=group_name)

    print(f'...{group_name} created.')

    # set base permissions for each group

    if group_name == Epilepsy12UserGroup.PATIENT or group_name == Epilepsy12UserGroup.PARENT:
        permission_names = [
            'can_consent_to_audit_participation',
            'can_approve_audit_data_submission'
        ]
        for name in permission_names:
            permission = Permission.objects.get(codename=name)
            group.permissions.add(permission)
    elif group_name == Epilepsy12UserGroup.LEAD_CLINICIAN or group_name == Epilepsy12UserGroup.CLINICIAN or group_name == Epilepsy12UserGroup.CENTRE_ADMINISTRATOR:
        permission_names = [
            "can_view_case_named_centre",
            "can_view_named_centre_audit_items",
            "can_view_users_in_named_centres"
        ]
        for name in permission_names:
            permission = Permission.objects.get(codename=name)
            group.permissions.add(permission)

        if group_name == Epilepsy12UserGroup.CENTRE_ADMINISTRATOR:
            permission_names = [
                "can_create_case_named_centre",
                "can_update_case_named_centre",
                "can_delete_case_named_centre",
                "can_lock_case_named_centre",
                "can_register_case_named_centre",
                "can_delete_registration_named_centre",
                "can_edit_named_centre_audit_items",
                "can_delete_named_centre_audit_items",
                "can_create_named_centre_audit_items",
                "can_allocate_named_centre",
                "can_create_new_user_in_named_centres",
                "can_delete_user_in_named_centres",
                "can_update_user_in_named_centres",
                "can_update_role_in_named_centres",
                "can_create_new_role_in_named_centres"
            ]
        elif group_name == Epilepsy12UserGroup.LEAD_CLINICIAN:
            permission_names = [
                "can_update_case_named_centre",
                "can_delete_case_named_centre",
                "can_lock_case_named_centre",
                "can_register_case_named_centre",
                "can_delete_registration_named_centre",
                "can_edit_named_centre_audit_items",
                "can_delete_named_centre_audit_items",
                "can_create_named_centre_audit_items"
            ]
        elif group_name == Epilepsy12UserGroup.CLINICIAN:
            permission_names = [
                "can_update_case_named_centre",
                "can_lock_case_named_centre",
                "can_edit_named_centre_audit_items",
                "can_delete_named_centre_audit_items",
                "can_create_named_centre_audit_items"
            ]
        for name in permission_names:
            permission = Permission.objects.get(codename=name)
            group.permissions.add(permission)
    elif group_name == group_name == Epilepsy12UserGroup.AUDIT_LEAD_ADMINISTRATOR or group_name == Epilepsy12UserGroup.AUDIT_ADMINISTRATOR or group_name == Epilepsy12UserGroup.AUDIT_ANALYST:
        permission_names = [
            "can_view_case_all_centres",
            "can_view_all_centre_audit_items",
            "can_view_users_in_all_centres"
        ]
        for name in permission_names:
            permission = Permission.objects.get(codename=name)
            group.permissions.add(permission)

        if group_name == Epilepsy12UserGroup.AUDIT_LEAD_ADMINISTRATOR:
            permission_names = [
                "can_create_case_all_centres",
                "can_update_case_all_centres",
                "can_delete_case_all_centres",
                "can_lock_case_all_centres",
                "can_register_case_all_centres",
                "can_delete_registration_all_centres",
                "can_edit_all_centre_audit_items",
                "can_delete_all_centre_audit_items",
                "can_create_all_centre_audit_items",
                "can_allocate_all_centres",
                "can_create_new_user_in_all_centres",
                "can_delete_user_in_all_centres",
                "can_update_user_in_all_centres",
                "can_update_role_in_all_centres",
                "can_create_new_role_in_all_centres"
            ]
        elif group_name == Epilepsy12UserGroup.AUDIT_ADMINISTRATOR:
            permission_names = [
                "can_create_case_all_centres",
                "can_update_case_all_centres",
                "can_delete_case_all_centres",
                "can_lock_case_all_centres",
                "can_register_case_all_centres",
                "can_delete_registration_all_centres",
                "can_allocate_all_centres",
                "can_create_new_user_in_all_centres",
                "can_update_user_in_all_centres",
                "can_update_role_in_all_centres"
            ]
        elif group_name == Epilepsy12UserGroup.AUDIT_ANALYST:
            permission_names = [
                "can_download_data_tables"
            ]
        for name in permission_names:
            permission = Permission.objects.get(codename=name)
            group.permissions.add(permission)
    else:
        raise Exception("Group does not exist to allocate roles to.")

    print(f'...permissions allocated to {group_name}')


def run_hospitals_seed():
    # this adds all the English hospitals from JSON in the constants folder
    # There are also lists of hospitals across northern ireland, wales and scotland, but the JSON has a different structure
    added = 0
    for index, hospital in enumerate(ALL_HOSPITALS):
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
            print("Exception at "+hospital["OrganisationName"])
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
