from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from ...constants import GROUPS
from epilepsy12.constants.user_types import (
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
    PATIENT_ACCESS,
    TRUST_AUDIT_TEAM_EDIT_ACCESS,
    TRUST_AUDIT_TEAM_FULL_ACCESS,
    TRUST_AUDIT_TEAM_VIEW_ONLY,
    CAN_CONSENT_TO_AUDIT_PARTICIPATION,
    CAN_APPROVE_ELIGIBILITY,
    CAN_REMOVE_APPROVAL_OF_ELIGIBILITY,
    CAN_REGISTER_CHILD_IN_EPILEPSY12,
    CAN_UNREGISTER_CHILD_IN_EPILEPSY12,
    CAN_ALLOCATE_EPILEPSY12_LEAD_CENTRE,
    CAN_TRANSFER_EPILEPSY12_LEAD_CENTRE,
    CAN_EDIT_EPILEPSY12_LEAD_CENTRE,
    CAN_DELETE_EPILEPSY12_LEAD_CENTRE,
    CAN_APPROVE_ELIGIBILITY,
    CAN_REMOVE_APPROVAL_OF_ELIGIBILITY,
    CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING,
    CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING,
    CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT,
)
from epilepsy12.models import (
    AntiEpilepsyMedicine,
    Assessment,
    AuditProgress,
    Comorbidity,
    EpilepsyContext,
    Episode,
    FirstPaediatricAssessment,
    Investigations,
    Management,
    MultiaxialDiagnosis,
    Syndrome,
    Registration,
    Case,
    Organisation,
    Keyword,
    Site,
    Epilepsy12User,
)


def groups_seeder(
    run_create_groups=False, add_permissions_to_existing_groups=False, verbose=True
):
    caseContentType = ContentType.objects.get_for_model(Case)
    registrationContentType = ContentType.objects.get_for_model(Registration)
    first_paediatric_assessmentContentType = ContentType.objects.get_for_model(
        FirstPaediatricAssessment
    )
    epilepsy_contextContentType = ContentType.objects.get_for_model(EpilepsyContext)
    multiaxial_diagnosisContentType = ContentType.objects.get_for_model(
        MultiaxialDiagnosis
    )
    episodeContentType = ContentType.objects.get_for_model(Episode)
    syndromeContentType = ContentType.objects.get_for_model(Syndrome)
    comorbidityContentType = ContentType.objects.get_for_model(Comorbidity)
    assessmentContentType = ContentType.objects.get_for_model(Assessment)
    investigationsContentType = ContentType.objects.get_for_model(Investigations)
    managementContentType = ContentType.objects.get_for_model(Management)
    siteContentType = ContentType.objects.get_for_model(Site)
    antiepilepsymedicineContentType = ContentType.objects.get_for_model(
        AntiEpilepsyMedicine
    )
    organisationContentType = ContentType.objects.get_for_model(Organisation)
    keywordContentType = ContentType.objects.get_for_model(Keyword)
    auditprogressContentType = ContentType.objects.get_for_model(AuditProgress)
    epilepsy12userContentType = ContentType.objects.get_for_model(Epilepsy12User)

    VIEW_PERMISSIONS = [
        {"codename": "view_case", "content_type": caseContentType},
        {"codename": "view_registration", "content_type": registrationContentType},
        {
            "codename": "view_firstpaediatricassessment",
            "content_type": first_paediatric_assessmentContentType,
        },
        {
            "codename": "view_epilepsycontext",
            "content_type": epilepsy_contextContentType,
        },
        {
            "codename": "view_multiaxialdiagnosis",
            "content_type": multiaxial_diagnosisContentType,
        },
        {"codename": "view_episode", "content_type": episodeContentType},
        {"codename": "view_syndrome", "content_type": syndromeContentType},
        {"codename": "view_comorbidity", "content_type": comorbidityContentType},
        {"codename": "view_assessment", "content_type": assessmentContentType},
        {"codename": "view_investigations", "content_type": investigationsContentType},
        {"codename": "view_management", "content_type": managementContentType},
        {
            "codename": "view_antiepilepsymedicine",
            "content_type": antiepilepsymedicineContentType,
        },
        {"codename": "view_site", "content_type": siteContentType},
        {"codename": "view_organisation", "content_type": organisationContentType},
        {"codename": "view_keyword", "content_type": keywordContentType},
        {"codename": "view_auditprogress", "content_type": auditprogressContentType},
        {"codename": "view_epilepsy12user", "content_type": epilepsy12userContentType},
    ]

    EDITOR_PERMISSIONS = [
        {"codename": "change_case", "content_type": caseContentType},
        {"codename": "add_case", "content_type": caseContentType},
        {"codename": "change_registration", "content_type": registrationContentType},
        {"codename": "add_registration", "content_type": registrationContentType},
        {
            "codename": "can_register_child_in_epilepsy12",
            "content_type": registrationContentType,
        },
        {
            "codename": "can_unregister_child_in_epilepsy12",
            "content_type": registrationContentType,
        },
        {
            "codename": "can_approve_eligibility",
            "content_type": registrationContentType,
        },
        {
            "codename": "change_firstpaediatricassessment",
            "content_type": first_paediatric_assessmentContentType,
        },
        {
            "codename": "add_firstpaediatricassessment",
            "content_type": first_paediatric_assessmentContentType,
        },
        {
            "codename": "view_epilepsycontext",
            "content_type": epilepsy_contextContentType,
        },
        {
            "codename": "change_epilepsycontext",
            "content_type": epilepsy_contextContentType,
        },
        {
            "codename": "add_epilepsycontext",
            "content_type": epilepsy_contextContentType,
        },
        {
            "codename": "change_multiaxialdiagnosis",
            "content_type": multiaxial_diagnosisContentType,
        },
        {
            "codename": "add_multiaxialdiagnosis",
            "content_type": multiaxial_diagnosisContentType,
        },
        {"codename": "change_episode", "content_type": episodeContentType},
        {"codename": "add_episode", "content_type": episodeContentType},
        {"codename": "change_syndrome", "content_type": syndromeContentType},
        {"codename": "add_syndrome", "content_type": syndromeContentType},
        {"codename": "change_comorbidity", "content_type": comorbidityContentType},
        {"codename": "add_comorbidity", "content_type": comorbidityContentType},
        {"codename": "change_assessment", "content_type": assessmentContentType},
        {"codename": "add_assessment", "content_type": assessmentContentType},
        {
            "codename": "change_investigations",
            "content_type": investigationsContentType,
        },
        {"codename": "add_investigations", "content_type": investigationsContentType},
        {"codename": "change_management", "content_type": managementContentType},
        {"codename": "add_management", "content_type": managementContentType},
        {
            "codename": "change_antiepilepsymedicine",
            "content_type": antiepilepsymedicineContentType,
        },
        {
            "codename": "add_antiepilepsymedicine",
            "content_type": antiepilepsymedicineContentType,
        },
        {"codename": "change_site", "content_type": siteContentType},
        {"codename": "add_site", "content_type": siteContentType},
        {"codename": "add_epilepsy12user", "content_type": epilepsy12userContentType},
        {
            "codename": "change_epilepsy12user",
            "content_type": epilepsy12userContentType,
        },
    ]

    FULL_ACCESS_PERMISSIONS = [
        {"codename": "delete_case", "content_type": caseContentType},
        {"codename": "delete_registration", "content_type": registrationContentType},
        {
            "codename": "delete_firstpaediatricassessment",
            "content_type": first_paediatric_assessmentContentType,
        },
        {
            "codename": "delete_epilepsycontext",
            "content_type": epilepsy_contextContentType,
        },
        {
            "codename": "delete_multiaxialdiagnosis",
            "content_type": multiaxial_diagnosisContentType,
        },
        {"codename": "delete_episode", "content_type": episodeContentType},
        {"codename": "delete_syndrome", "content_type": syndromeContentType},
        {"codename": "delete_comorbidity", "content_type": comorbidityContentType},
        {"codename": "delete_assessment", "content_type": assessmentContentType},
        {
            "codename": "delete_investigations",
            "content_type": investigationsContentType,
        },
        {"codename": "delete_management", "content_type": managementContentType},
        {"codename": "delete_site", "content_type": siteContentType},
        {
            "codename": "delete_antiepilepsymedicine",
            "content_type": antiepilepsymedicineContentType,
        },
    ]

    EPILEPSY12_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS = []

    EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS = [
        {
            "codename": CAN_APPROVE_ELIGIBILITY[0],
            "content_type": registrationContentType,
        },
        {
            "codename": CAN_REMOVE_APPROVAL_OF_ELIGIBILITY[0],
            "content_type": registrationContentType,
        },
        {
            "codename": CAN_REGISTER_CHILD_IN_EPILEPSY12[0],
            "content_type": registrationContentType,
        },
        {
            "codename": CAN_UNREGISTER_CHILD_IN_EPILEPSY12[0],
            "content_type": registrationContentType,
        },
        {
            "codename": CAN_TRANSFER_EPILEPSY12_LEAD_CENTRE[0],
            "content_type": siteContentType,
        },
        {
            "codename": CAN_CONSENT_TO_AUDIT_PARTICIPATION[0],
            "content_type": caseContentType,
        },
        {
            "codename": CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING[0],
            "content_type": caseContentType,
        },
        {
            "codename": CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING[0],
            "content_type": caseContentType,
        },
        {
            "codename": CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT[0],
            "content_type": caseContentType,
        },
    ]

    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS = [
        {"codename": "change_organisation", "content_type": organisationContentType},
        {"codename": "add_organisation", "content_type": organisationContentType},
        {"codename": "delete_organisation", "content_type": organisationContentType},
        {"codename": "change_keyword", "content_type": keywordContentType},
        {"codename": "add_keyword", "content_type": keywordContentType},
        {"codename": "delete_keyword", "content_type": keywordContentType},
        {"codename": "delete_auditprogress", "content_type": auditprogressContentType},
        {"codename": "change_auditprogress", "content_type": auditprogressContentType},
        {"codename": "add_auditprogress", "content_type": auditprogressContentType},
        {
            "codename": "delete_epilepsy12user",
            "content_type": epilepsy12userContentType,
        },
        {
            "codename": CAN_DELETE_EPILEPSY12_LEAD_CENTRE[0],
            "content_type": siteContentType,
        },
        {
            "codename": CAN_EDIT_EPILEPSY12_LEAD_CENTRE[0],
            "content_type": siteContentType,
        },
        {
            "codename": CAN_ALLOCATE_EPILEPSY12_LEAD_CENTRE[0],
            "content_type": siteContentType,
        },
    ]

    TRUST_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS = []

    TRUST_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS = [
        {
            "codename": CAN_APPROVE_ELIGIBILITY[0],
            "content_type": registrationContentType,
        },
        {
            "codename": CAN_REGISTER_CHILD_IN_EPILEPSY12[0],
            "content_type": registrationContentType,
        },
        {
            "codename": CAN_TRANSFER_EPILEPSY12_LEAD_CENTRE[0],
            "content_type": siteContentType,
        },
        {
            "codename": CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING[0],
            "content_type": caseContentType,
        },
        {
            "codename": CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT[0],
            "content_type": caseContentType,
        },
    ]

    TRUST_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS = [
        {
            "codename": CAN_APPROVE_ELIGIBILITY[0],
            "content_type": registrationContentType,
        },
        {
            "codename": CAN_REGISTER_CHILD_IN_EPILEPSY12[0],
            "content_type": registrationContentType,
        },
        {
            "codename": CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING[0],
            "content_type": caseContentType,
        },
        {
            "codename": CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT[0],
            "content_type": caseContentType,
        },
    ]

    PATIENT_ACCESS_PERMISSIONS = [
        {
            "codename": CAN_CONSENT_TO_AUDIT_PARTICIPATION[0],
            "content_type": caseContentType,
        },
    ]

    def initialize_permissions(apps, schema_editor):
        """
        This function is run in migrations/0002_create_groups.py as an initial
        data migration at project initialization. it sets up some basic model-level
        permissions for different groups when the project is initialised.

        6 groups. Loop through and add custom
        """

        # Permissions have to be created before applying them
        for app_config in apps.get_app_configs(apps, schema_editor):
            app_config.models_module = True
            create_permissions(app_config, verbosity=0)
            app_config.models_module = None

    if add_permissions_to_existing_groups:
        for group in GROUPS:
            if verbose:
                print(f"...adding permissions to {group}...")
            # add permissions to group
            newGroup = Group.objects.filter(name=group).get()

            if group == EPILEPSY12_AUDIT_TEAM_FULL_ACCESS:
                # custom permissions
                add_permissions_to_group(
                    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS, newGroup
                )
                # basic permissions
                add_permissions_to_group(VIEW_PERMISSIONS, newGroup)
                add_permissions_to_group(EDITOR_PERMISSIONS, newGroup)
                add_permissions_to_group(FULL_ACCESS_PERMISSIONS, newGroup)

            elif group == TRUST_AUDIT_TEAM_VIEW_ONLY:
                # custom permissions
                add_permissions_to_group(
                    TRUST_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS, newGroup
                )
                # basic permissions
                add_permissions_to_group(VIEW_PERMISSIONS, newGroup)

            elif group == TRUST_AUDIT_TEAM_EDIT_ACCESS:
                # custom permissions
                add_permissions_to_group(
                    TRUST_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS, newGroup
                )
                add_permissions_to_group(
                    TRUST_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS, newGroup
                )
                # basic permissions
                add_permissions_to_group(VIEW_PERMISSIONS, newGroup)
                add_permissions_to_group(EDITOR_PERMISSIONS, newGroup)

            elif group == TRUST_AUDIT_TEAM_FULL_ACCESS:
                # custom permissions
                add_permissions_to_group(
                    TRUST_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS, newGroup
                )
                add_permissions_to_group(
                    TRUST_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS, newGroup
                )
                add_permissions_to_group(
                    TRUST_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS, newGroup
                )
                # basic permissions
                add_permissions_to_group(VIEW_PERMISSIONS, newGroup)
                add_permissions_to_group(EDITOR_PERMISSIONS, newGroup)
                add_permissions_to_group(FULL_ACCESS_PERMISSIONS, newGroup)

            elif group == PATIENT_ACCESS:
                # custom permissions
                add_permissions_to_group(PATIENT_ACCESS_PERMISSIONS, newGroup)
                # basic permissions
                add_permissions_to_group(VIEW_PERMISSIONS, newGroup)

            else:
                if verbose:
                    print("Error: group does not exist!")

    def add_permissions_to_group(permissions_list, group_to_add):
        for permission in permissions_list:
            codename = permission.get("codename")
            content_type = permission.get("content_type")
            newPermission = Permission.objects.get(
                codename=codename, content_type=content_type
            )
            if group_to_add.permissions.filter(codename=codename).exists():
                if verbose:
                    print(f"{codename} already exists for this group. Skipping...")
            else:
                if verbose:
                    print(f"...Adding {codename}")
                group_to_add.permissions.add(newPermission)

    if run_create_groups:
        for group in GROUPS:
            if not Group.objects.filter(name=group).exists():
                if verbose:
                    print(f"...creating group: {group}")
                try:
                    newGroup = Group.objects.create(name=group)
                except Exception as error:
                    if verbose:
                        print(error)
                    error = True

                if verbose:
                    print(f"...adding permissions to {group}...")
                # add permissions to group

                if group == EPILEPSY12_AUDIT_TEAM_FULL_ACCESS:
                    # custom permissions
                    add_permissions_to_group(
                        EPILEPSY12_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS, newGroup
                    )
                    add_permissions_to_group(
                        EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS, newGroup
                    )
                    add_permissions_to_group(
                        EPILEPSY12_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS, newGroup
                    )
                    # basic permissions
                    add_permissions_to_group(VIEW_PERMISSIONS, newGroup)
                    add_permissions_to_group(EDITOR_PERMISSIONS, newGroup)
                    add_permissions_to_group(FULL_ACCESS_PERMISSIONS, newGroup)

                elif group == TRUST_AUDIT_TEAM_VIEW_ONLY:
                    # custom permissions
                    add_permissions_to_group(
                        TRUST_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS, newGroup
                    )
                    # basic permissions
                    add_permissions_to_group(VIEW_PERMISSIONS, newGroup)

                elif group == TRUST_AUDIT_TEAM_EDIT_ACCESS:
                    # custom permissions
                    add_permissions_to_group(
                        TRUST_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS, newGroup
                    )
                    add_permissions_to_group(
                        TRUST_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS, newGroup
                    )
                    # basic permissions
                    add_permissions_to_group(VIEW_PERMISSIONS, newGroup)
                    add_permissions_to_group(EDITOR_PERMISSIONS, newGroup)

                elif group == TRUST_AUDIT_TEAM_FULL_ACCESS:
                    # custom permissions
                    add_permissions_to_group(
                        TRUST_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS, newGroup
                    )
                    add_permissions_to_group(
                        TRUST_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS, newGroup
                    )
                    add_permissions_to_group(
                        TRUST_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS, newGroup
                    )
                    # basic permissions
                    add_permissions_to_group(VIEW_PERMISSIONS, newGroup)
                    add_permissions_to_group(EDITOR_PERMISSIONS, newGroup)
                    add_permissions_to_group(FULL_ACCESS_PERMISSIONS, newGroup)

                elif group == PATIENT_ACCESS:
                    # custom permissions
                    add_permissions_to_group(PATIENT_ACCESS_PERMISSIONS, newGroup)
                    # basic permissions
                    add_permissions_to_group(VIEW_PERMISSIONS, newGroup)

                else:
                    if verbose:
                        print("Error: group does not exist!")
            else:
                if verbose:
                    print(f"{group} already exists. Skipping...")
        if not verbose:
            print("groups_seeder(verbose=False), no output, groups seeded.")
