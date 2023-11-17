# python
from random import randint, choice
from datetime import date
from random import randint

import nhs_number

from django.core.management.base import BaseCommand

from ...general_functions import (
    get_current_cohort_data,
    return_random_postcode,
    random_date,
)
from ...constants import (
    ETHNICITIES,
)
from ...models import Organisation, Case, Site, Registration, LocalHealthBoard, Trust
from .create_groups import groups_seeder
from .create_e12_records import create_epilepsy12_record, create_registrations
from epilepsy12.tests.factories import E12CaseFactory
from .old_pt_data_scripts import load_and_prep_data, get_default_org_from_record
from epilepsy12.general_functions.postcode import is_valid_postcode


class Command(BaseCommand):
    help = "seed database with organisation trust data for testing and development."

    def add_arguments(self, parser):
        parser.add_argument("-m", "--mode", type=str, help="Mode")
        parser.add_argument(
            "-c",
            "--cases",
            nargs="?",
            type=int,
            help="Indicates the number of children to be created",
            default=50,
        )

    def handle(self, *args, **options):
        if options["mode"] == "cases":
            cases = options["cases"]
            self.stdout.write("seeding with dummy case data...")
            run_dummy_cases_seed(cases=cases)

        elif options["mode"] == "seed_registrations":
            self.stdout.write(
                "register cases in audit and complete all fields with random answers..."
            )
            run_registrations()
        elif options["mode"] == "seed_groups_and_permissions":
            self.stdout.write("setting up groups and permissions...")
            groups_seeder(run_create_groups=True)
        elif options["mode"] == "add_permissions_to_existing_groups":
            self.stdout.write("adding permissions to groups...")
            groups_seeder(add_permissions_to_existing_groups=True)
        elif options["mode"] == "delete_all_groups_and_recreate":
            self.stdout.write("deleting all groups/permissions and reallocating...")
        elif options["mode"] == "add_existing_medicines_as_foreign_keys":
            self.stdout.write("replacing medicines with medicine entity...")
        elif options["mode"] == "upload_old_patient_data":
            self.stdout.write("Uploading old patient data.")
            insert_old_pt_data()

        else:
            self.stdout.write("No options supplied...")
        # print("\033[38;2;17;167;142m")
        # self.stdout.write(image())
        # print("\033[38;2;17;167;107m")
        # self.stdout.write("done.")


def run_dummy_cases_seed(verbose=True, cases=50):
    if verbose:
        print("\033[33m", f"Seeding {cases} fictional cases...", "\033[33m")
    # there should not be any cases yet, but sometimes seed gets run more than once
    if Case.objects.all().exists():
        if verbose:
            print("Cases already exist. Skipping this step...")
        return

    if cases is None or cases == 0:
        cases = 50

    different_organisations = [
        "RGT01",
        "RBS25",
        "RQM01",
        "RCF22",
        "7A2AJ",
        "7A6BJ",
        "7A6AV",
    ]
    organisations_list = Organisation.objects.filter(
        ods_code__in=different_organisations
    ).order_by("name")
    for org in organisations_list:
        num_cases_to_seed_in_org = int(cases / len(different_organisations))
        print(f"Creating {num_cases_to_seed_in_org} Cases in {org}")

        # Create random attributes
        random_date = date(randint(2005, 2021), randint(1, 12), randint(1, 28))
        date_of_birth = random_date
        sex = randint(1, 2)
        seed_male = True if sex == 1 else False
        seed_female = True if sex == 2 else False
        random_ethnicity = randint(0, len(choice(ETHNICITIES)))
        ethnicity = ETHNICITIES[random_ethnicity][0]
        postcode = return_random_postcode(
            country_boundary_identifier=org.country.boundary_identifier
        )
        postcode = return_random_postcode(
            country_boundary_identifier=org.country.boundary_identifier
        )

        E12CaseFactory.create_batch(
            num_cases_to_seed_in_org,
            locked=False,
            sex=sex,
            date_of_birth=date_of_birth,
            postcode=postcode,
            ethnicity=ethnicity,
            organisations__organisation=org,
            **{
                "seed_male": seed_male,
                "seed_female": seed_female,
            },
        )


def run_registrations(verbose=True):
    """
    Calling function to register all cases in Epilepsy12 and complete all fields with random answers
    """
    if verbose:
        print("\033[33m", "Registering fictional cases in Epilepsy12...", "\033[33m")

    create_registrations(verbose=verbose)

    complete_registrations(verbose=verbose)

    if not verbose:
        print(
            "run_registrations(verbose=False), no output, cases registered and completed."
        )


def complete_registrations(verbose=True):
    """
    Loop through the registrations and score all fields
    """
    if verbose:
        print(
            "\033[33m",
            "Completing all the Epilepsy12 fields for the fictional cases...",
            "\033[33m",
        )
    current_cohort = get_current_cohort_data()
    for registration in Registration.objects.all():
        registration.first_paediatric_assessment_date = random_date(
            start=current_cohort["cohort_start_date"], end=date.today()
        )
        registration.eligibility_criteria_met = True
        registration.save()

        create_epilepsy12_record(registration_instance=registration, verbose=verbose)


def insert_old_pt_data():
    print(
        "\033[33m",
        "Running clean and conversion of old patient data...",
        "\033[33m",
    )

    data_for_db = load_and_prep_data(csv_path="epilepsy12/management/commands/data.csv")

    print(
        "\033[33m",
        "Success! Inserting records into db...",
        "\033[33m",
    )

    for record in data_for_db:
        # Validation steps
        if not nhs_number.is_valid(record["nhs_number"]):
            print(f'{record["nhs_number"]} is invalid. Skipping insertion...')
            continue

        if not is_valid_postcode(record["postcode"]):
            print(
                f"({record['nhs_number']=}) {record['postcode']} is invalid. Skipping"
            )

        # NOTE TODO: remove TEMP!!!
        if Case.objects.filter(nhs_number=record["nhs_number"]).exists():
            print(
                f'{Case.objects.get(nhs_number=record["nhs_number"]).nhs_number} already exists. Deleting for debug...'
            )
            Case.objects.get(nhs_number=record["nhs_number"]).delete()

        inserted_patient = Case.objects.create(
            locked=False,
            nhs_number=record["nhs_number"],
            first_name=record["first_name"],
            surname=record["surname"],
            sex=record["sex"],
            date_of_birth=record["date_of_birth"],
            postcode=record["postcode"],
            ethnicity=record["ethnicity"],
        )

        # NOTE TODO: remove TEMP!!!
        if Site.objects.filter(case=inserted_patient).exists():
            print(
                f"{Site.objects.get(case=inserted_patient)} already exists. Deleting for debug..."
            )
            Site.objects.get(case=inserted_patient).delete()

        # Get organisation
        try:
            organisation = Organisation.objects.get(ods_code=record["organisationcode"])
        except Exception as e:
            print(
                f'Couldn\'t find organisation for {record["organisationcode"]}. Skipping {record["nhs_number"]}'
            )

        # allocate the child to the organisation supplied as primary E12 centre
        Site.objects.create(
            site_is_actively_involved_in_epilepsy_care=True,
            site_is_primary_centre_of_epilepsy_care=True,
            organisation=organisation,
            case=inserted_patient,
        )

        print(
            f"Successfully inserted {inserted_patient.first_name} {inserted_patient.surname}"
        )


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
