# python
from random import randint, choice
from datetime import date
from random import randint
import logging
from dateutil.relativedelta import relativedelta
from epilepsy12.models import AuditPeriod
from epilepsy12.general_functions.date_functions import nth_tuesday_of_year
from epilepsy12.constants.audit_period_dates import AUDIT_PERIODS

from django.core.management.base import BaseCommand

# Logging setup
logger = logging.getLogger(__name__)

from ...general_functions import (
    return_random_postcode,
    random_date,
)
from ...constants import (
    ETHNICITIES,
)
from ...models import Organisation, Case, Registration
from .create_groups import groups_seeder
from .create_e12_records import create_epilepsy12_record, create_registrations
from epilepsy12.tests.factories import E12CaseFactory
from epilepsy12.management.commands.old_pt_data_scripts import (
    insert_old_pt_data,
)
from epilepsy12.management.commands.user_scripts import insert_user_data
from epilepsy12.common_view_functions import _seed_all_aggregation_models

ORGANISATION_SEED_LIST = [
    "RJZ01",  # King's College Hospital
    "RGT01",  # Addenbrooks
    "RBS25",  # Alderhey
    "RQM01",  # Chelsea and Westminster
    "RCF22",  # Airedale
    "7A2AJ",  # Bronglais
    "7A6BJ",  # Chepstow Community
    "7A6AV",  # Ysbyty Ystrad Fawr
    "RGT1W",  # Jersey General Hospital
]


class Command(BaseCommand):
    help = "seed database with organisation trust data for testing and development."

    def add_arguments(self, parser):
        parser.add_argument(
            "-m",
            "--mode",
            type=str,
            help="Mode - seed options to include: cases, seed_registrations, seed_groups_and_permissions, upload_old_patient_data, upload_user_data, add_new_epilepsy_causes",
        )
        parser.add_argument(
            "-c",
            "--cases",
            nargs="?",
            type=int,
            help="Indicates the number of children to be created. Parameter for cases mode Default is 50.",
            default=50,
        )
        parser.add_argument(
            "-ns",
            "--noskip",
            action="store_true",
            help="Optional parameter. Set to disable skipping cases if they already exist",
            default=False,
        )
        parser.add_argument(
            "-ct",
            "--cohort",
            nargs="?",
            type=int,
            help="Indicates the cohort to create create registrations under. Note cannot be less than 4.",
            default=8,
        )
        parser.add_argument(
            "-fy",
            "--full_year",
            action="store_true",
            help="Optional parameter. Set to ensure all cases being registered have completed a full year of care. Default is True.",
            default=False,
        )
        parser.add_argument(
            "-orgs",
            "--organisations",
            nargs="+",
            help="Optional List of Organisation ODS codes.",
            type=str,
        )
        parser.add_argument(
            "--up_to_cohort",
            nargs="?",
            help="To seed audit periods up to a given cohort.",
            type=int
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force update of existing audit periods.",
        )


    def handle(self, *args, **options):
        if options["mode"] == "cases":
            cases = options["cases"]
            noskip = options.get("noskip", True)
            organisations_list = (
                options["organisations"]
                if options["organisations"] is not None
                else ORGANISATION_SEED_LIST
            )
            self.stdout.write("seeding with dummy case data...")
            run_dummy_cases_seed(
                cases=cases, organisations=organisations_list, noskip=noskip
            )
            print(image())

        elif options["mode"] == "seed_registrations":
            self.stdout.write(
                "register cases in audit and complete all fields with random answers..."
            )
            cohort = options["cohort"]
            completed_full_year = options["full_year"]
            run_registrations(cohort=cohort, full_year=completed_full_year)
            _seed_all_aggregation_models()
            print(image())
        elif options["mode"] == "seed_groups_and_permissions":
            self.stdout.write("setting up groups and permissions...")
            groups_seeder()
            print(image())
        elif options["mode"] == "upload_old_patient_data":
            self.stdout.write("Uploading old patient data.")
            insert_old_pt_data()
        elif options["mode"] == "upload_user_data":
            self.stdout.write("Uploading user data.")
            insert_user_data()
        elif options["mode"] == "seed_audit_periods":
            up_to_cohort = options["up_to_cohort"]
            force = options["force"]
            seed_audit_periods(up_to_cohort=up_to_cohort, force=force)
            print(image())
        else:
            self.stdout.write("No options supplied...")


def run_dummy_cases_seed(cases, organisations, noskip, verbose=True):

    if verbose:
        print("\033[33m", f"Seeding {cases} fictional cases...", "\033[33m")
    # there should not be any cases yet, but sometimes seed gets run more than once
    if Case.objects.all().exists() and not noskip:
        if verbose:
            print("Cases already exist. Skipping this step...")
        return

    if cases is None or cases == 0:
        cases = 50

    organisations_list = Organisation.objects.filter(
        ods_code__in=organisations, active=True
    ).order_by("name")
    for org in organisations_list:
        num_cases_to_seed_in_org = int(cases / len(organisations))
        print(f"Creating {num_cases_to_seed_in_org} Cases in {org}")

        # Check if the organisation is in Jersey - this is important for generating postcodes and URNs rather than NHS Numbers
        is_jersey = org.country.boundary_identifier == "JEY"

        # Create random attributes
        random_date = date(randint(2005, 2021), randint(1, 12), randint(1, 28))
        date_of_birth = random_date
        sex = randint(1, 2)
        seed_male = True if sex == 1 else False
        seed_female = True if sex == 2 else False
        random_ethnicity = randint(0, len(choice(ETHNICITIES)))
        ethnicity = ETHNICITIES[random_ethnicity][0]
        postcode = return_random_postcode(
            country_boundary_identifier=org.country.boundary_identifier,
            is_jersey=is_jersey,
        )
        index_of_multiple_deprivation_quintile = randint(1, 5)

        E12CaseFactory.create_batch(
            num_cases_to_seed_in_org,
            locked=False,
            sex=sex,
            date_of_birth=date_of_birth,
            postcode=postcode,
            ethnicity=ethnicity,
            index_of_multiple_deprivation_quintile=index_of_multiple_deprivation_quintile,
            organisations__organisation=org,
            **{
                "seed_male": seed_male,
                "seed_female": seed_female,
            },
            is_jersey=is_jersey,
        )


def run_registrations(verbose=True, cohort=7, full_year=False):
    """
    Calling function to register all cases in Epilepsy12 and complete all fields with random answers
    """
    if verbose:
        print("\033[33m", "Registering fictional cases in Epilepsy12...", "\033[33m")

    create_registrations(verbose=verbose)

    complete_registrations(verbose=verbose, cohort=cohort, full_year=full_year)

    if not verbose:
        print(
            "run_registrations(verbose=False), no output, cases registered and completed."
        )


def complete_registrations(verbose=True, cohort=None, full_year=False):
    """
    Loop through the registrations and score all fields
    """
    if verbose:
        print(
            "\033[33m",
            "Completing all the Epilepsy12 fields for the fictional cases...",
            "\033[33m",
        )

    # Cohort number if today is date of FPA
    current_recruiting = AuditPeriod.objects.currently_recruiting()
    current_cohort_number = current_recruiting.cohort_number if current_recruiting else None

    if cohort is None:
        # Generate cohort data for current cohort
        target_cohort = current_cohort_number
    else:
        target_cohort = cohort

    audit_period = AuditPeriod.objects.by_cohort(target_cohort)
    if audit_period is None:
        logger.warning(
            f"No AuditPeriod found for cohort {target_cohort}; skipping registrations."
        )
        return
    cohort_data = audit_period.as_cohort_card_dict()

    for registration in Registration.objects.all():

        if cohort is not None and cohort != current_cohort_number:
            fpa_date = random_date(
                start=cohort_data["cohort_start_date"],
                end=cohort_data["cohort_end_date"],
            )
        else:
            fpa_date = random_date(
                start=cohort_data["cohort_start_date"],
                end=date.today(),
            )

        if full_year:
            # this flag ensures any registrations include a full year of care
            if cohort_data["cohort_start_date"] + relativedelta(years=1) > date.today():
                # It is not possible to generate registrations that are complete as they would be in the future
                logger.warning(
                    "It is not possible for registrations to be complete for this cohort as they would be in the future."
                )
            else:
                while fpa_date + relativedelta(years=1) >= date.today():
                    # regenerate any dates that cannot be complete
                    fpa_date = random_date(
                        start=cohort_data["cohort_start_date"],
                        end=cohort_data["cohort_end_date"],
                    )

        registration.first_paediatric_assessment_date = fpa_date
        registration.eligibility_criteria_met = True
        registration.save()

        create_epilepsy12_record(registration_instance=registration, verbose=verbose)



def seed_audit_periods(up_to_cohort: int=0, force: bool=False):
    """Create any missing AuditPeriods up to the given cohort using the
    E12 convention. NEVER updates existing rows: deadlines may have been
    deliberately edited by the RCPCH audit team UNLESS the --force option is used."""
    if not up_to_cohort:
        # default: everything up to the currently recruiting cohort
        today = date.today()
        up_to_cohort = today.year - 2016

    if up_to_cohort < 4:
        print("No need to seed audit periods: cohort is before 4.")
        return
    for n in range(4, up_to_cohort + 1):
        if n < 10: # for cohorts upto 9 we use the hard coded list
            (rec_start, rec_end, dc_end, deadline) = AUDIT_PERIODS[n]
        else:
            rec_start = date(2016 + n + 1, 1, 1)
            rec_end = date(2016 + n + 1, 12, 31)
            dc_end = date(2016 + n + 2, 12, 31)
            deadline = nth_tuesday_of_year(dc_end.year + 1, n=2)
        if force:
            audit_period, created = AuditPeriod.objects.update_or_create(
                cohort_number=n,
                defaults={
                    "recruitment_start_date": rec_start,
                    "recruitment_end_date": rec_end,
                    "data_collection_end_date": dc_end,
                    "submission_deadline": deadline,
                    "slug": f"cohort-{n}",
                    "is_visible": True,
                },
            )
        else:
            audit_period, created = AuditPeriod.objects.get_or_create(
                cohort_number=n,
                defaults={
                    "recruitment_start_date": rec_start,
                    "recruitment_end_date": rec_end,
                    "data_collection_end_date": dc_end,
                    "submission_deadline": deadline,
                    "slug": f"cohort-{n}",
                    "is_visible": True,
                },
            )
        force_string = " (forced)" if force else ""
        if created:
            print(f"Created AuditPeriod for cohort {n} - {audit_period}{force_string}")
        else:
            print(f"Using existing AuditPeriod for cohort {n} - {audit_period}{force_string}")



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
