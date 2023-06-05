# python
from random import randint, choice
from datetime import date
from dateutil.relativedelta import relativedelta
from random import randint
from django.core.management.base import BaseCommand
from ...general_functions import (
    get_current_cohort_data,
    generate_nhs_number,
    return_random_postcode,
)


from ...constants import (
    ETHNICITIES,
)
from ...models import (
    Organisation,
    Case,
    Site,
    Registration,
)

from ...general_functions import (
    random_date,
)
from .create_groups import groups_seeder
from .create_e12_records import create_epilepsy12_record, create_registrations


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

        else:
            self.stdout.write("No options supplied...")
        print("\033[38;2;17;167;142m")
        self.stdout.write(image())
        print("\033[38;2;17;167;107m")
        self.stdout.write("done.")


def run_dummy_cases_seed(verbose=True, cases=50):
    added = 0
    if verbose:
        print("\033[33m", "Seeding fictional cases...", "\033[33m")
    # there should not be any cases yet, but sometimes seed gets run more than once
    if Case.objects.all().exists():
        if verbose:
            print("Cases already exist. Skipping this step...")
        return

    if cases is None or cases == 0:
        cases = 50

    # for index in range(len(DUMMY_NAMES) - 1): # commented out line populates all the names, not just first 20
    for index in range(0, cases):  # first 20 names
        random_date = date(randint(2005, 2021), randint(1, 12), randint(1, 28))
        nhs_number = generate_nhs_number()
        sex = randint(1, 2)
        random_ethnicity = randint(0, len(choice(ETHNICITIES)))
        if sex == 2:
            first_name = "Dolly"
            surname = f"Shepherd-{index}"
        else:
            first_name = "Agent"
            surname = f"Smith-{index}"

        date_of_birth = random_date
        postcode = return_random_postcode()
        ethnicity = ETHNICITIES[random_ethnicity][0]

        # get a random organisation
        if index < 50:
            organisation = Organisation.objects.get(ODSCode="RGT01")  # King's Mill
        else:
            organisation = Organisation.objects.order_by(
                "?"
            ).first()  # random organisation

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
                ethnicity=ethnicity,
            )
            new_case.save()
        except Exception as e:
            if verbose:
                print(f"Error saving case: {e}")
            case_has_error = True

        if not case_has_error:
            try:
                new_site = Site.objects.create(
                    organisation=organisation,
                    site_is_actively_involved_in_epilepsy_care=True,
                    site_is_primary_centre_of_epilepsy_care=True,
                    case=new_case,
                )
                new_site.save()
            except Exception as e:
                if verbose:
                    print(f"Error saving site: {e}")

            added += 1
            if verbose:
                print(
                    f"{new_case.first_name} {new_case.surname} at {new_site.organisation.OrganisationName} ({new_site.organisation.ParentOrganisation_OrganisationName})..."
                )
    print(f"Saved {added} cases.")


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
        registration.registration_date = random_date(
            start=current_cohort["cohort_start_date"], end=date.today()
        )
        registration.eligibility_criteria_met = True
        registration.save()

        create_epilepsy12_record(registration_instance=registration, verbose=verbose)


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
