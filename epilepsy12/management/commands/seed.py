from random import randint, getrandbits, choice
from datetime import date
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from epilepsy12.constants.user_types import EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS, EPILEPSY12_AUDIT_TEAM_FULL_ACCESS, EPILEPSY12_AUDIT_TEAM_VIEW_ONLY, PATIENT_ACCESS, TRUST_AUDIT_TEAM_EDIT_ACCESS, TRUST_AUDIT_TEAM_FULL_ACCESS, TRUST_AUDIT_TEAM_VIEW_ONLY, CAN_ONLY_VIEW_CHILD_CASE_DATA, CAN_ONLY_VIEW_GENERAL_PAEDIATRIC_CENTRE, CAN_ONLY_VIEW_TERTIARY_NEUROLOGY_CENTRE, CAN_ONLY_VIEW_CHILDRENS_EPILEPSY_SURGERY_CENTRE, CAN_VIEW_CHILD_NHS_NUMBER, CAN_VIEW_CHILD_DATE_OF_BIRTH, CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING, CAN_APPROVE_ELIGIBILITY, CAN_REMOVE_APPROVAL_OF_ELIGIBILITY, CAN_REGISTER_CHILD_IN_EPILEPSY12, CAN_UNREGISTER_CHILD_IN_EPILEPSY12, CAN_ONLY_VIEW_GENERAL_PAEDIATRIC_CENTRE, CAN_ALLOCATE_GENERAL_PAEDIATRIC_CENTRE, CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE, CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE, CAN_EDIT_TERTIARY_NEUROLOGY_CENTRE, CAN_CONFIRM_CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET, CAN_ALLOCATE_CHILDRENS_EPILEPSY_SURGERY_CENTRE, CAN_EDIT_CHILDRENS_EPILEPSY_SURGERY_CENTRE, CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING, CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT, CAN_APPROVE_ELIGIBILITY, CAN_REMOVE_APPROVAL_OF_ELIGIBILITY, CAN_REGISTER_CHILD_IN_EPILEPSY12, CAN_UNREGISTER_CHILD_IN_EPILEPSY12, CAN_ALLOCATE_GENERAL_PAEDIATRIC_CENTRE, CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE, CAN_DELETE_GENERAL_PAEDIATRIC_CENTRE, CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE, CAN_EDIT_TERTIARY_NEUROLOGY_CENTRE, CAN_DELETE_TERTIARY_NEUROLOGY_CENTRE, CAN_CONFIRM_CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET, CAN_DELETE_CHILDRENS_EPILEPSY_SURGERY_CENTRE, CAN_CONSENT_TO_AUDIT_PARTICIPATION
from epilepsy12.models import AntiEpilepsyMedicine, Assessment, AuditProgress, Comorbidity, EpilepsyContext, Episode, FirstPaediatricAssessment, Investigations, Management, MultiaxialDiagnosis, Syndrome
from ...constants import ETHNICITIES, DUMMY_NAMES, GROUPS
from ...models import HospitalTrust, Keyword, Case, Site, Registration
from ...constants import ALL_HOSPITALS, KEYWORDS
from ...general_functions import random_postcodes

# globals
caseContentType = ContentType.objects.get_for_model(Case)
registrationContentType = ContentType.objects.get_for_model(
    Registration)
first_paediatric_assessmentContentType = ContentType.objects.get_for_model(
    FirstPaediatricAssessment)
epilepsy_contextContentType = ContentType.objects.get_for_model(
    EpilepsyContext)
multiaxial_diagnosisContentType = ContentType.objects.get_for_model(
    MultiaxialDiagnosis)
episodeContentType = ContentType.objects.get_for_model(Episode)
syndromeContentType = ContentType.objects.get_for_model(Syndrome)
comorbidityContentType = ContentType.objects.get_for_model(
    Comorbidity)
assessmentContentType = ContentType.objects.get_for_model(
    Assessment)
investigationsContentType = ContentType.objects.get_for_model(
    Investigations)
managementContentType = ContentType.objects.get_for_model(
    Management)
siteContentType = ContentType.objects.get_for_model(
    Site)
antiepilepsymedicineContentType = ContentType.objects.get_for_model(
    AntiEpilepsyMedicine)
hospital_trustContentType = ContentType.objects.get_for_model(
    HospitalTrust)
keywordContentType = ContentType.objects.get_for_model(
    Keyword)
auditprogressContentType = ContentType.objects.get_for_model(
    AuditProgress)

VIEW_PERMISSIONS = [
    {'codename': 'view_case',
     'content_type': caseContentType},
    {'codename': 'view_registration',
     'content_type': registrationContentType},
    {'codename': 'view_FirstPaediatricAssessment',
     'content_type': initial_assessmfirst_paediatric_assessmentContentType},
    {'codename': 'view_epilepsycontext',
     'content_type': epilepsy_contextContentType},
    {'codename': 'view_multiaxialdiagnosis',
     'content_type': multiaxial_diagnosisContentType},
    {'codename': 'view_episode',
     'content_type': episodeContentType},
    {'codename': 'view_syndrome',
     'content_type': syndromeContentType},
    {'codename': 'view_comorbidity',
     'content_type': comorbidityContentType},
    {'codename': 'view_assessment',
     'content_type': assessmentContentType},
    {'codename': 'view_investigations',
     'content_type': investigationsContentType},
    {'codename': 'view_management',
     'content_type': managementContentType},
    {'codename': 'view_antiepilepsymedicine',
     'content_type': antiepilepsymedicineContentType},
    {'codename': 'view_site',
     'content_type': siteContentType},
]

EDITOR_PERMISSIONS = [
    {'codename': 'view_case', 'content_type': caseContentType},
    {'codename': 'change_case',
     'content_type': caseContentType},
    {'codename': 'add_case',
     'content_type': caseContentType},
    {'codename': 'view_registration',
     'content_type': registrationContentType},
    {'codename': 'change_registration',
     'content_type': registrationContentType},
    {'codename': 'add_registration',
     'content_type': registrationContentType},
    {'codename': 'can_register_child_in_epilepsy12',
     'content_type': registrationContentType},
    {'codename': 'can_unregister_child_in_epilepsy12',
     'content_type': registrationContentType},
    {'codename': 'can_approve_eligibility',
     'content_type': registrationContentType},
    {'codename': 'view_FirstPaediatricAssessment',
     'content_type': first_paediatric_assessmentContentType},
    {'codename': 'change_FirstPaediatricAssessment',
     'content_type': first_paediatric_assessmentContentType},
    {'codename': 'add_FirstPaediatricAssessment',
     'content_type': first_paediatric_assessmentContentType},
    {'codename': 'view_epilepsycontext',
     'content_type': epilepsy_contextContentType},
    {'codename': 'change_epilepsycontext',
     'content_type': epilepsy_contextContentType},
    {'codename': 'add_epilepsycontext',
     'content_type': epilepsy_contextContentType},
    {'codename': 'view_multiaxialdiagnosis',
     'content_type': multiaxial_diagnosisContentType},
    {'codename': 'change_multiaxialdiagnosis',
     'content_type': multiaxial_diagnosisContentType},
    {'codename': 'add_multiaxialdiagnosis',
     'content_type': multiaxial_diagnosisContentType},
    {'codename': 'view_episode',
     'content_type': episodeContentType},
    {'codename': 'change_episode',
     'content_type': episodeContentType},
    {'codename': 'add_episode',
     'content_type': episodeContentType},
    {'codename': 'view_syndrome',
     'content_type': syndromeContentType},
    {'codename': 'change_syndrome',
     'content_type': syndromeContentType},
    {'codename': 'add_syndrome',
     'content_type': syndromeContentType},
    {'codename': 'view_comorbidity',
     'content_type': comorbidityContentType},
    {'codename': 'change_comorbidity',
     'content_type': comorbidityContentType},
    {'codename': 'add_comorbidity',
     'content_type': comorbidityContentType},
    {'codename': 'view_assessment',
     'content_type': assessmentContentType},
    {'codename': 'change_assessment',
     'content_type': assessmentContentType},
    {'codename': 'add_assessment',
     'content_type': assessmentContentType},
    {'codename': 'view_investigations',
     'content_type': investigationsContentType},
    {'codename': 'change_investigations',
     'content_type': investigationsContentType},
    {'codename': 'add_investigations',
     'content_type': investigationsContentType},
    {'codename': 'view_management',
     'content_type': managementContentType},
    {'codename': 'change_management',
     'content_type': managementContentType},
    {'codename': 'add_management',
     'content_type': managementContentType},
    {'codename': 'view_antiepilepsymedicine',
     'content_type': antiepilepsymedicineContentType},
    {'codename': 'change_antiepilepsymedicine',
     'content_type': antiepilepsymedicineContentType},
    {'codename': 'add_antiepilepsymedicine',
     'content_type': antiepilepsymedicineContentType},
    {'codename': 'view_site',
     'content_type': siteContentType},
    {'codename': 'change_site',
     'content_type': siteContentType},
    {'codename': 'add_site',
     'content_type': siteContentType},
]

FULL_ACCESS_PERMISSIONS = [
    {'codename': 'delete_case', 'content_type': caseContentType},
    {'codename': 'delete_registration',
        'content_type': registrationContentType},
    {'codename': 'delete_FirstPaediatricAssessment',
        'content_type': first_paediatric_assessmentContentType},
    {'codename': 'delete_epilepsycontext',
        'content_type': epilepsy_contextContentType},
    {'codename': 'delete_multiaxialdiagnosis',
        'content_type': multiaxial_diagnosisContentType},
    {'codename': 'delete_episode', 'content_type': episodeContentType},
    {'codename': 'delete_syndrome',
        'content_type': syndromeContentType},
    {'codename': 'delete_comorbidity',
        'content_type': comorbidityContentType},
    {'codename': 'delete_assessment',
        'content_type': assessmentContentType},
    {'codename': 'delete_investigations',
        'content_type': investigationsContentType},
    {'codename': 'delete_management',
        'content_type': managementContentType},
    {'codename': 'delete_site', 'content_type': siteContentType},
    {'codename': 'delete_antiepilepsymedicine',
        'content_type': antiepilepsymedicineContentType},
]

SUPERADMIN_PERMISSIONS = [
    {'codename': 'view_hospitaltrust',
        'content_type': hospital_trustContentType},
    {'codename': 'change_hospitaltrust',
        'content_type': hospital_trustContentType},
    {'codename': 'add_hospitaltrust',
        'content_type': hospital_trustContentType},
    {'codename': 'delete_hospitaltrust',
        'content_type': hospital_trustContentType},
    {'codename': 'view_keyword',
        'content_type': keywordContentType},
    {'codename': 'change_keyword',
        'content_type': keywordContentType},
    {'codename': 'add_keyword',
        'content_type': keywordContentType},
    {'codename': 'delete_keyword',
        'content_type': keywordContentType},
    {'codename': 'delete_auditprogress',
        'content_type': auditprogressContentType},
    {'codename': 'view_auditprogress',
        'content_type': auditprogressContentType},
    {'codename': 'change_auditprogress',
        'content_type': auditprogressContentType},
    {'codename': 'add_auditprogress',
        'content_type': auditprogressContentType},
]

EPILEPSY12_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS = [
    {'codename': CAN_ONLY_VIEW_CHILD_CASE_DATA[0],
        'content_type': caseContentType},
    {'codename': CAN_ONLY_VIEW_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_ONLY_VIEW_TERTIARY_NEUROLOGY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_ONLY_VIEW_CHILDRENS_EPILEPSY_SURGERY_CENTRE[0],
        'content_type': assessmentContentType}

]

EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS = [
    {'codename': CAN_VIEW_CHILD_NHS_NUMBER[0],
        'content_type': caseContentType},
    {'codename': CAN_VIEW_CHILD_DATE_OF_BIRTH[0],
        'content_type': caseContentType},
    {'codename': CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING[0],
        'content_type': caseContentType},
    {'codename': CAN_APPROVE_ELIGIBILITY[0],
        'content_type': registrationContentType},
    {'codename': CAN_REMOVE_APPROVAL_OF_ELIGIBILITY[0],
        'content_type': registrationContentType},
    {'codename': CAN_REGISTER_CHILD_IN_EPILEPSY12[0],
        'content_type': registrationContentType},
    {'codename': CAN_UNREGISTER_CHILD_IN_EPILEPSY12[0],
        'content_type': registrationContentType},

    {'codename': CAN_ONLY_VIEW_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': registrationContentType},
    {'codename': CAN_ALLOCATE_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': registrationContentType},
    {'codename': CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': registrationContentType},

    {'codename': CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_EDIT_TERTIARY_NEUROLOGY_CENTRE[0],
        'content_type': assessmentContentType},

    {'codename': CAN_CONFIRM_CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET[
        0], 'content_type': assessmentContentType},
    {'codename': CAN_ALLOCATE_CHILDRENS_EPILEPSY_SURGERY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_EDIT_CHILDRENS_EPILEPSY_SURGERY_CENTRE[0],
        'content_type': assessmentContentType},

]

EPILEPSY12_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS = [
    {'codename': CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING[0],
        'content_type': caseContentType},
    {'codename': CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT[0],
        'content_type': caseContentType},
    {'codename': CAN_APPROVE_ELIGIBILITY[0],
        'content_type': registrationContentType},
    {'codename': CAN_REMOVE_APPROVAL_OF_ELIGIBILITY[0],
        'content_type': registrationContentType},
    {'codename': CAN_REGISTER_CHILD_IN_EPILEPSY12[0],
        'content_type': registrationContentType},
    {'codename': CAN_UNREGISTER_CHILD_IN_EPILEPSY12[0],
        'content_type': registrationContentType},

    {'codename': CAN_ALLOCATE_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': registrationContentType},
    {'codename': CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': registrationContentType},
    {'codename': CAN_DELETE_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': registrationContentType},

    {'codename': CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_EDIT_TERTIARY_NEUROLOGY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_DELETE_TERTIARY_NEUROLOGY_CENTRE[0],
        'content_type': assessmentContentType},

    {'codename': CAN_CONFIRM_CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET[
        0], 'content_type': assessmentContentType},
    {'codename': CAN_ALLOCATE_CHILDRENS_EPILEPSY_SURGERY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_EDIT_CHILDRENS_EPILEPSY_SURGERY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_DELETE_CHILDRENS_EPILEPSY_SURGERY_CENTRE[0],
        'content_type': assessmentContentType},

]

TRUST_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS = [
    {'codename': CAN_VIEW_CHILD_NHS_NUMBER[0],
        'content_type': caseContentType},
    {'codename': CAN_VIEW_CHILD_DATE_OF_BIRTH[0],
        'content_type': caseContentType},
    {'codename': CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING[0],
        'content_type': caseContentType},

    {'codename': CAN_ONLY_VIEW_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': registrationContentType},
    {'codename': CAN_ONLY_VIEW_TERTIARY_NEUROLOGY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_ONLY_VIEW_CHILDRENS_EPILEPSY_SURGERY_CENTRE[0],
        'content_type': assessmentContentType},

    {'codename': CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': registrationContentType},
    {'codename': CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_EDIT_TERTIARY_NEUROLOGY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_EDIT_CHILDRENS_EPILEPSY_SURGERY_CENTRE[0],
        'content_type': assessmentContentType},

]

TRUST_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS = [
    {'codename': CAN_VIEW_CHILD_NHS_NUMBER[0],
        'content_type': caseContentType},
    {'codename': CAN_VIEW_CHILD_DATE_OF_BIRTH[0],
        'content_type': caseContentType},
    {'codename': CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING[0],
        'content_type': caseContentType},

    {'codename': CAN_APPROVE_ELIGIBILITY[0],
        'content_type': registrationContentType},
    {'codename': CAN_REMOVE_APPROVAL_OF_ELIGIBILITY[0],
        'content_type': registrationContentType},
    {'codename': CAN_REGISTER_CHILD_IN_EPILEPSY12[0],
        'content_type': registrationContentType},
    {'codename': CAN_UNREGISTER_CHILD_IN_EPILEPSY12[0],
        'content_type': registrationContentType},

    {'codename': CAN_ALLOCATE_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': registrationContentType},
    {'codename': CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': registrationContentType},

    {'codename': CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_EDIT_TERTIARY_NEUROLOGY_CENTRE[0],
        'content_type': assessmentContentType},

    {'codename': CAN_CONFIRM_CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET[
        0], 'content_type': assessmentContentType},
    {'codename': CAN_ALLOCATE_CHILDRENS_EPILEPSY_SURGERY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_EDIT_CHILDRENS_EPILEPSY_SURGERY_CENTRE[0],
        'content_type': assessmentContentType},

]

TRUST_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS = [
    {'codename': CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING[0],
        'content_type': caseContentType},
    {'codename': CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT[0],
        'content_type': caseContentType},
    {'codename': CAN_APPROVE_ELIGIBILITY[0],
        'content_type': registrationContentType},
    {'codename': CAN_REMOVE_APPROVAL_OF_ELIGIBILITY[0],
        'content_type': registrationContentType},
    {'codename': CAN_REGISTER_CHILD_IN_EPILEPSY12[0],
        'content_type': registrationContentType},
    {'codename': CAN_UNREGISTER_CHILD_IN_EPILEPSY12[0],
        'content_type': registrationContentType},

    {'codename': CAN_ALLOCATE_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': registrationContentType},
    {'codename': CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': registrationContentType},
    {'codename': CAN_DELETE_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': registrationContentType},

    {'codename': CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_EDIT_TERTIARY_NEUROLOGY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_DELETE_TERTIARY_NEUROLOGY_CENTRE[0],
        'content_type': assessmentContentType},

    {'codename': CAN_CONFIRM_CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET[
        0], 'content_type': assessmentContentType},
    {'codename': CAN_ALLOCATE_CHILDRENS_EPILEPSY_SURGERY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_EDIT_CHILDRENS_EPILEPSY_SURGERY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_DELETE_CHILDRENS_EPILEPSY_SURGERY_CENTRE[0],
        'content_type': assessmentContentType},

]

PATIENT_ACCESS_PERMISSIONS = [
    {'codename': CAN_ONLY_VIEW_CHILD_CASE_DATA[0],
        'content_type': caseContentType},

    {'codename': CAN_ONLY_VIEW_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': registrationContentType},
    {'codename': CAN_ONLY_VIEW_TERTIARY_NEUROLOGY_CENTRE[0],
        'content_type': assessmentContentType},
    {'codename': CAN_ONLY_VIEW_CHILDRENS_EPILEPSY_SURGERY_CENTRE[0],
        'content_type': assessmentContentType},

    {'codename': CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT[0],
        'content_type': caseContentType},
    {'codename': CAN_CONSENT_TO_AUDIT_PARTICIPATION[0],
        'content_type': caseContentType},

    {'codename': CAN_ONLY_VIEW_GENERAL_PAEDIATRIC_CENTRE[0],
        'content_type': registrationContentType},
]


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


def add_permissions_to_existing_groups():
    for group in GROUPS:
        print(f'...adding permissions to {group}...')
        # add permissions to group
        newGroup = Group.objects.filter(name=group).get()

        if group == EPILEPSY12_AUDIT_TEAM_VIEW_ONLY:
            # custom permissions
            add_permissions_to_group(
                EPILEPSY12_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS, newGroup)
            # basic permissions
            add_permissions_to_group(VIEW_PERMISSIONS, newGroup)

        elif group == EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS:
            # custom permissions
            add_permissions_to_group(
                EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS, newGroup)
            # basic permissions
            add_permissions_to_group(EDITOR_PERMISSIONS, newGroup)

        elif group == EPILEPSY12_AUDIT_TEAM_FULL_ACCESS:
            # custom permissions
            add_permissions_to_group(
                EPILEPSY12_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS, newGroup)
            # basic permissions
            add_permissions_to_group(EDITOR_PERMISSIONS, newGroup)
            add_permissions_to_group(FULL_ACCESS_PERMISSIONS, newGroup)

        elif group == TRUST_AUDIT_TEAM_VIEW_ONLY:
            # custom permissions
            add_permissions_to_group(
                TRUST_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS, newGroup)
            # basic permissions
            add_permissions_to_group(VIEW_PERMISSIONS, newGroup)

        elif group == TRUST_AUDIT_TEAM_EDIT_ACCESS:
            # custom permissions
            add_permissions_to_group(
                TRUST_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS, newGroup)
            # basic permissions
            add_permissions_to_group(EDITOR_PERMISSIONS, newGroup)

        elif group == TRUST_AUDIT_TEAM_FULL_ACCESS:
            # custom permissions
            add_permissions_to_group(
                TRUST_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS, newGroup)
            # basic permissions
            add_permissions_to_group(EDITOR_PERMISSIONS, newGroup)
            add_permissions_to_group(FULL_ACCESS_PERMISSIONS, newGroup)

        elif group == PATIENT_ACCESS:
            # custom permissions
            add_permissions_to_group(
                PATIENT_ACCESS_PERMISSIONS, newGroup)
            # basic permissions
            add_permissions_to_group(VIEW_PERMISSIONS, newGroup)

        else:
            print("Error: group does not exist!")


def create_groups():
    for group in GROUPS:
        if not Group.objects.filter(name=group).exists():
            print(f'...creating group: {group}')
            try:
                newGroup = Group.objects.create(name=group)
            except Exception as error:
                print(error)
                error = True

            print(f'...adding permissions to {group}...')
            # add permissions to group

            if group == EPILEPSY12_AUDIT_TEAM_VIEW_ONLY:
                # custom permissions
                add_permissions_to_group(
                    EPILEPSY12_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS, newGroup)
                # basic permissions
                add_permissions_to_group(VIEW_PERMISSIONS, newGroup)

            elif group == EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS:
                # custom permissions
                add_permissions_to_group(
                    EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS, newGroup)
                # basic permissions
                add_permissions_to_group(EDITOR_PERMISSIONS, newGroup)

            elif group == EPILEPSY12_AUDIT_TEAM_FULL_ACCESS:
                # custom permissions
                add_permissions_to_group(
                    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS, newGroup)
                # basic permissions
                add_permissions_to_group(EDITOR_PERMISSIONS, newGroup)
                add_permissions_to_group(FULL_ACCESS_PERMISSIONS, newGroup)

            elif group == TRUST_AUDIT_TEAM_VIEW_ONLY:
                # custom permissions
                add_permissions_to_group(
                    TRUST_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS, newGroup)
                # basic permissions
                add_permissions_to_group(VIEW_PERMISSIONS, newGroup)

            elif group == TRUST_AUDIT_TEAM_EDIT_ACCESS:
                # custom permissions
                add_permissions_to_group(
                    TRUST_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS, newGroup)
                # basic permissions
                add_permissions_to_group(EDITOR_PERMISSIONS, newGroup)

            elif group == TRUST_AUDIT_TEAM_FULL_ACCESS:
                # custom permissions
                add_permissions_to_group(
                    TRUST_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS, newGroup)
                # basic permissions
                add_permissions_to_group(EDITOR_PERMISSIONS, newGroup)
                add_permissions_to_group(FULL_ACCESS_PERMISSIONS, newGroup)

            elif group == PATIENT_ACCESS:
                # custom permissions
                add_permissions_to_group(
                    PATIENT_ACCESS_PERMISSIONS, newGroup)
                # basic permissions
                add_permissions_to_group(VIEW_PERMISSIONS, newGroup)

            else:
                print("Error: group does not exist!")
        else:
            print(f'{group} already exists. Skipping...')


def add_permissions_to_group(permissions_list, group_to_add):
    for permission in permissions_list:
        codename = permission.get('codename')
        content_type = permission.get('content_type')
        print(f'...Adding {codename}')
        newPermission = Permission.objects.get(
            codename=codename,
            content_type=content_type
        )
        group_to_add.permissions.add(newPermission)


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
