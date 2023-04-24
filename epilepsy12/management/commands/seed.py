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
        
        if (options['mode'] == 'seed_groups_and_permissions'):
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

        else:
            self.stdout.write('No options supplied...')
        print('\033[38;2;17;167;142m')
        self.stdout.write(image())
        print('\033[38;2;17;167;107m')
        self.stdout.write('done.')

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
