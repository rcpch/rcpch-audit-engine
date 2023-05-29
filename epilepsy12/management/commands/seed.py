# python
from random import randint, choice
from datetime import date
from dateutil.relativedelta import relativedelta
from random import randint
from django.core.management.base import BaseCommand
from ...general_functions import get_current_cohort_data


from ...constants import (
    ETHNICITIES,
    DUMMY_NAMES,
    SYNDROMES,
    SNOMED_BENZODIAZEPINE_TYPES,
    SNOMED_ANTIEPILEPSY_MEDICINE_TYPES,
    OPEN_UK_NETWORKS,
    RCPCH_ORGANISATIONS,
)
from ...models import (
    Organisation,
    Keyword,
    Case,
    Site,
    Registration,
    SyndromeEntity,
    EpilepsyCauseEntity,
    ComorbidityEntity,
    MedicineEntity,
    AntiEpilepsyMedicine,
    IntegratedCareBoardEntity,
    OPENUKNetworkEntity,
    NHSRegionEntity,
    ONSRegionEntity,
    ONSCountryEntity,
)
from ...constants import (
    ALL_HOSPITALS,
    KEYWORDS,
    WELSH_HOSPITALS,
    INTEGRATED_CARE_BOARDS_LOCAL_AUTHORITIES,
    WELSH_REGIONS,
    COUNTRY_CODES,
    UK_ONS_REGIONS,
)
from ...general_functions import (
    random_postcodes,
    random_date,
    first_tuesday_in_january,
    current_cohort_start_date,
    fetch_ecl,
    fetch_paediatric_neurodisability_outpatient_diagnosis_simple_reference_set,
    ons_region_for_postcode,
)
from .create_groups import groups_seeder
from .create_e12_records import create_epilepsy12_record, create_registrations

class Command(BaseCommand):
    help = "seed database with organisation trust data for testing and development."

    def add_arguments(self, parser):
        parser.add_argument("--mode", type=str, help="Mode")

    def handle(self, *args, **options):
        if options["mode"] == "seed_dummy_cases":
            self.stdout.write("seeding with dummy case data...")
            run_dummy_cases_seed()
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


def run_dummy_cases_seed(verbose=True):
    added = 0
    if verbose: print("\033[33m", "Seeding fictional cases...", "\033[33m")
    # there should not be any cases yet, but sometimes seed gets run more than once
    if Case.objects.all().exists():
        if verbose: print("Cases already exist. Skipping this step...")
        return

    postcode_list = random_postcodes.generate_postcodes(requested_number=100)

    random_organisations = ["RX1LK", "RK5BC"]

    """
    Commented out section creates cases across 10 organisations, the first being Addenbrooke's
    # first populate Addenbrooke's for ease of dev testing
    for _ in range(1, 11):
        random_organisations.append(
            Organisation.objects.get(ODSCode='RGT01'))

    # seed the remaining 9
    for j in range(9):
        random_organisation = Organisation.objects.order_by("?").first()
        for i in range(1, 11):
            random_organisations.append(random_organisation)
    """

    # for index in range(len(DUMMY_NAMES) - 1): # commented out line populates all the names, not just first 20
    for index in range(0, 99):  # first 20 names
        random_date = date(randint(2005, 2021), randint(1, 12), randint(1, 28))
        nhs_number = randint(1000000000, 9999999999)
        first_name = DUMMY_NAMES[index]["firstname"]
        surname = DUMMY_NAMES[index]["lastname"]
        gender_object = DUMMY_NAMES[index]["gender"]
        if gender_object == "m":
            sex = 1
        else:
            sex = 2
        date_of_birth = random_date
        postcode = postcode_list[index]
        ethnicity = choice(ETHNICITIES)[0]

        # get a random organisation
        if index < 50:
            # organisation = random_organisations[index] # line used if populating random hospitals
            organisation = Organisation.objects.get(ODSCode=random_organisations[0])
        else:
            organisation = Organisation.objects.get(ODSCode=random_organisations[1])

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
            if verbose: print(f"Error saving case: {e}")
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
                if verbose: print(f"Error saving site: {e}")

            added += 1
            if verbose: print(
                f"{new_case.first_name} {new_case.surname} at {new_site.organisation.OrganisationName} ({new_site.organisation.ParentOrganisation_OrganisationName})..."
            )
    print(f"Saved {added} cases.")


def run_registrations(verbose=True):

    """
    Calling function to register all cases in Epilepsy12 and complete all fields with random answers
    """
    if verbose: print("\033[33m", "Registering fictional cases in Epilepsy12...", "\033[33m")

    create_registrations(verbose=verbose)

    complete_registrations(verbose=verbose)
    
    if not verbose: print("run_registrations(verbose=False), no output, cases registered and completed.")


def complete_registrations(verbose=True):
    """
    Loop through the registrations and score all fields
    """
    if verbose: print(
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
