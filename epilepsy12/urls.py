from django.conf.urls import include
from .views import *
from .views.api.epilepsy12user_viewset import Epilepsy12UserViewSet
from .views.api.case_viewset import CaseViewSet
from .views.api.registration_viewset import RegistrationViewSet
from .views.api.entity_viewsets import (
    EpilepsyCauseEntityViewSet,
    KeywordViewSet,
    OrganisationViewSet,
    AntiEpilepsyMedicineViewSet,
)
from .views.api.episode_viewset import EpisodeViewSet
from .views.api.syndrome_viewset import SyndromeViewSet, SyndromeViewSet
from .views.api.comorbidity_viewset import ComorbidityViewSet, ComorbidityEntityViewSet
from .views.api.assessment_viewset import AssessmentViewSet
from .views.api.management_viewset import ManagementViewSet
from .views.api.investigations_viewset import InvestigationsViewSet
from .views.api.site_viewset import SiteViewSet
from .views.api.audit_progress_viewset import AuditProgressViewSet

from rest_framework import routers, urls
from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path
from django.contrib.auth import urls as auth_urls
from django.contrib.auth import views as auth_views
from .forms import Epilepsy12UserUpdatePasswordForm

# router = routers.DefaultRouter()

"""
These are all the endpoints for the API - currently commented out but can be brought in one by one as tests are added.
router.register(r"epilepsy12users", viewset=Epilepsy12UserViewSet)
router.register(r"cases", viewset=CaseViewSet)
router.register(r"registration", viewset=RegistrationViewSet)

router.register(
    r"epilepsy_cause_entity",
    viewset=EpilepsyCauseEntityViewSet,
    basename="epilepsycauseentity",
)
router.register(r"episode", viewset=EpisodeViewSet)
router.register(r"syndrome", viewset=SyndromeViewSet)
router.register(r"comorbidity", viewset=ComorbidityViewSet)
router.register(r"assessment", viewset=AssessmentViewSet)
router.register(r"investigations", viewset=InvestigationsViewSet)
router.register(r"management", viewset=ManagementViewSet)
router.register(
    r"antiepilepsy_medicine",
    viewset=AntiEpilepsyMedicineViewSet,
    basename="antiepilepsymedicine",
)
router.register(r"site", viewset=SiteViewSet)
router.register(r"organisations", viewset=OrganisationViewSet)
router.register(r"keyword", viewset=KeywordViewSet)
router.register(
    r"audit_progress", viewset=AuditProgressViewSet, basename="auditprogress"
)
router.register(r"syndrome_entities", viewset=SyndromeViewSet, basename="syndromelist")
router.register(
    r"comorbidity_entities",
    viewset=ComorbidityEntityViewSet,
    basename="comorbidityentity",
)
"""


# Auth, login, password reset
user_patterns = [
    path("captcha/", include("captcha.urls")),
    path("account/", include(auth_urls)),
    path(
        "account/password-reset/",
        view=ResetPasswordView.as_view(),
        name="password_reset",
    ),
    path(
        "account/password-reset-confirm/<uidb64>/<token>",
        view=auth_views.PasswordResetConfirmView.as_view(
            form_class=Epilepsy12UserUpdatePasswordForm,
            template_name="registration/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),
    path(
        "organisation/<int:organisation_id>/epilepsy12_users/<int:epilepsy12_user_id>/logs",
        view=logs,
        name="logs",
    ),
    path(
        "organisation/<int:organisation_id>/epilepsy12_users/<int:epilepsy12_user_id>/log_list",
        view=log_list,
        name="log_list",
    ),
    path(
        "organisation/<int:organisation_id>/epilepsy12_user_list/",
        view=epilepsy12_user_list,
        name="epilepsy12_user_list",
    ),
    path(
        "organisation/<int:organisation_id>/full_e12user_list",
        view=all_epilepsy12_users_list,
        name="download_e12_users",
    ),
    path(
        "organisation/<int:organisation_id>/epilepsy12_users/<int:epilepsy12_user_id>/<str:user_type>/create",
        # accepts params organisation-staff or rcpch-staff
        view=create_epilepsy12_user,
        name="create_epilepsy12_user",
    ),
    path(
        "organisation/<int:organisation_id>/epilepsy12_users/<int:epilepsy12_user_id>/delete",
        view=delete_epilepsy12_user,
        name="delete_epilepsy12_user",
    ),
    path(
        "organisation/<int:organisation_id>/epilepsy12_users/<int:epilepsy12_user_id>/edit",
        view=edit_epilepsy12_user,
        name="edit_epilepsy12_user",
    ),
    # list and filter callbacks
    path(
        "organisation/<int:organisation_id>/filtered_epilepsy12_user_list",
        epilepsy12_user_list,
        name="filtered_epilepsy12_user_list",
    ),
    path(
        "organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_name_up",
        epilepsy12_user_list,
        name="sort_epilepsy12_users_by_name_up",
    ),
    path(
        "organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_name_down",
        epilepsy12_user_list,
        name="sort_epilepsy12_users_by_name_down",
    ),
    path(
        "organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_email_up",
        epilepsy12_user_list,
        name="sort_epilepsy12_users_by_email_up",
    ),
    path(
        "organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_email_down",
        epilepsy12_user_list,
        name="sort_epilepsy12_users_by_email_down",
    ),
    path(
        "organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_role_up",
        epilepsy12_user_list,
        name="sort_epilepsy12_users_by_role_up",
    ),
    path(
        "organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_role_down",
        epilepsy12_user_list,
        name="sort_epilepsy12_users_by_role_down",
    ),
    path(
        "organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_organisation_employer_up",
        epilepsy12_user_list,
        name="sort_epilepsy12_users_by_organisation_employer_up",
    ),
    path(
        "organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_organisation_employer_down",
        epilepsy12_user_list,
        name="sort_epilepsy12_users_by_organisation_employer_down",
    ),
]

redirect_patterns = [
    path("403", redirect_403, name="redirect_403"),
]

home_page_patterns = [
    path("", index, name="index"),
    path("database", view=database, name="database"),
    path("docs/", view=documentation, name="docs"),
]

case_patterns = [
    path("organisation/<int:organisation_id>/cases/", view=case_list, name="cases"),
    path(
        "organisation/<int:organisation_id>/case/<int:case_id>/update",
        view=update_case,
        name="update_case",
    ),
    path(
        "organisation/<int:organisation_id>/case/create",
        view=create_case,
        name="create_case",
    ),
    path(
        "organisation/<int:organisation_id>/case/unknown_postcode",
        view=unknown_postcode,
        name="unknown_postcode",
    ),
    path("case/<int:case_id>/register", register, name="register"),
    path(
        "case/<int:case_id>/case_performance_summary",
        view=case_performance_summary,
        name="case_performance_summary",
    ),
    path(
        "organisation/<int:organisation_id>/case/<int:case_id>/opt-out",
        view=opt_out,
        name="opt_out",
    ),
    path(
        "case/<int:case_id>/consent",
        view=consent,
        name="consent",
    ),
    path(
        "case/<int:case_id>/consent/<str:consent_type>/confirm",
        view=consent_confirmation,
        name="consent_confirmation",
    ),
    path(
        "organisation/<int:organisation_id>/case/<int:case_id>/submit",
        view=case_submit,
        name="case_submit",
    ),
    # case table - list and filter endpoints
    path(
        "htmx/filter_case_list/<organisation_id>",
        case_list,
        name="filter_case_list",
    ),
    path(
        "htmx/sort_by_nhs_number_up/<int:organisation_id>",
        case_list,
        name="sort_by_nhs_number_up",
    ),
    path(
        "htmx/sort_by_nhs_number_down/<int:organisation_id>",
        case_list,
        name="sort_by_nhs_number_down",
    ),
    path(
        "htmx/sort_by_sex_up/<int:organisation_id>",
        case_list,
        name="sort_by_sex_up",
    ),
    path(
        "htmx/sort_by_sex_down/<int:organisation_id>",
        case_list,
        name="sort_by_sex_down",
    ),
    path(
        "htmx/sort_by_name_up/<int:organisation_id>",
        case_list,
        name="sort_by_name_up",
    ),
    path(
        "htmx/sort_by_name_down/<int:organisation_id>",
        case_list,
        name="sort_by_name_down",
    ),
    path(
        "htmx/sort_by_id_up/<int:organisation_id>",
        case_list,
        name="sort_by_id_up",
    ),
    path(
        "htmx/sort_by_id_down/<int:organisation_id>",
        case_list,
        name="sort_by_id_down",
    ),
    path(
        "htmx/sort_by_deadline_up/<int:organisation_id>",
        case_list,
        name="sort_by_deadline_up",
    ),
    path(
        "htmx/sort_by_deadline_down/<int:organisation_id>",
        case_list,
        name="sort_by_deadline_down",
    ),
    path(
        "htmx/sort_by_cohort_up/<int:organisation_id>",
        case_list,
        name="sort_by_cohort_up",
    ),
    path(
        "htmx/sort_by_cohort_down/<int:organisation_id>",
        case_list,
        name="sort_by_cohort_down",
    ),
    path(
        "htmx/sort_by_days_remaining_before_submission_up/<int:organisation_id>",
        case_list,
        name="sort_by_days_remaining_before_submission_up",
    ),
    path(
        "htmx/sort_by_days_remaining_before_submission_down/<int:organisation_id>",
        case_list,
        name="sort_by_days_remaining_before_submission_down",
    ),
]

organisation_patterns = [
    path(
        "organisation/<int:organisation_id>/cases/view_preference/<str:template_name>",
        view=view_preference,
        name="view_preference",
    ),
    path(
        "organisation/<int:organisation_id>/cases/organisation_select/<str:template_name>",
        view=child_organisation_select,
        name="child_organisation_select",
    ),
    path(
        "organisation/<int:organisation_id>/summary",
        view=selected_organisation_summary,
        name="selected_organisation_summary",
    ),
    path(
        "selected_trust/<int:organisation_id>/kpis",
        view=selected_trust_kpis,
        name="selected_trust_kpis",
    ),
    path(
        "selected_trust/<int:organisation_id>/kpis/open",
        view=selected_trust_kpis_open,
        name="selected_trust_kpis_open",
    ),
    path(
        "selected_trust_kpis/<int:organisation_id>/select_kpi",
        view=selected_trust_select_kpi,
        name="selected_trust_select_kpi",
    ),
    path(
        "update_all_kpi_aggregation_models",
        view=aggregate_and_update_all_kpi_agg_models,
        name="aggregate_and_update_all_kpi_agg_models",
    ),
    path(
        "organisation/<int:organisation_id>/case_statistics",
        view=case_statistics,
        name="case_statistics",
    ),
    path(
        "organisation/<int:organisation_id>/open_access",
        view=open_access,
        name="open_access",
    ),
]

global_htmx_trigger_patterns = [
    path(
        "registration/<int:case_id>/registration_active/<str:active_template>",
        view=registration_active,
        name="registration_active",
    ),
    path("download_select", download_select, name="download_select"),
    path("<str:model_name>/download", download, name="download"),
]

first_paediatric_assessment_patterns = [
    path(
        "first_paediatric_assessment/<int:case_id>/edit",
        view=first_paediatric_assessment_views.first_paediatric_assessment,
        name="first_paediatric_assessment",
    ),
    path(
        "first_paediatric_assessment/<int:first_paediatric_assessment_id>/first_paediatric_assessment_in_acute_or_nonacute_setting",
        first_paediatric_assessment_in_acute_or_nonacute_setting,
        name="first_paediatric_assessment_in_acute_or_nonacute_setting",
    ),
    path(
        "first_paediatric_assessment/<int:first_paediatric_assessment_id>/has_number_of_episodes_since_the_first_been_documented",
        has_number_of_episodes_since_the_first_been_documented,
        name="has_number_of_episodes_since_the_first_been_documented",
    ),
    path(
        "first_paediatric_assessment/<int:first_paediatric_assessment_id>/general_examination_performed",
        general_examination_performed,
        name="general_examination_performed",
    ),
    path(
        "first_paediatric_assessment/<int:first_paediatric_assessment_id>/neurological_examination_performed",
        neurological_examination_performed,
        name="neurological_examination_performed",
    ),
    path(
        "first_paediatric_assessment/<int:first_paediatric_assessment_id>/developmental_learning_or_schooling_problems",
        developmental_learning_or_schooling_problems,
        name="developmental_learning_or_schooling_problems",
    ),
    path(
        "first_paediatric_assessment/<int:first_paediatric_assessment_id>/behavioural_or_emotional_problems",
        behavioural_or_emotional_problems,
        name="behavioural_or_emotional_problems",
    ),
]

assessment_patterns = [
    path(
        "assessment/<int:case_id>/", view=assessment_views.assessment, name="assessment"
    ),
    #     Consultant paediatrician fields
    path(
        "assessment/<int:assessment_id>/consultant_paediatrician_referral_made",
        consultant_paediatrician_referral_made,
        name="consultant_paediatrician_referral_made",
    ),
    path(
        "assessment/<int:assessment_id>/consultant_paediatrician_referral_date",
        consultant_paediatrician_referral_date,
        name="consultant_paediatrician_referral_date",
    ),
    path(
        "assessment/<int:assessment_id>/consultant_paediatrician_input_date",
        consultant_paediatrician_input_date,
        name="consultant_paediatrician_input_date",
    ),
    # general paediatric centre fields
    path(
        "assessment/<int:assessment_id>/general_paediatric_centre",
        general_paediatric_centre,
        name="general_paediatric_centre",
    ),
    path(
        "assessment/<int:assessment_id>/general_paediatric_centre/<int:site_id>/delete",
        delete_general_paediatric_centre,
        name="delete_general_paediatric_centre",
    ),
    path(
        "assessment/<int:assessment_id>/general_paediatric_centre/<int:site_id>/edit",
        edit_general_paediatric_centre,
        name="edit_general_paediatric_centre",
    ),
    path(
        "assessment/<int:assessment_id>/general_paediatric_centre/<int:site_id>/active/<str:action>",
        update_general_paediatric_centre_pressed,
        name="update_general_paediatric_centre_pressed",
    ),
    #     Consultant paediatric neurologist fields
    path(
        "assessment/<int:assessment_id>/paediatric_neurologist_referral_made",
        paediatric_neurologist_referral_made,
        name="paediatric_neurologist_referral_made",
    ),
    path(
        "assessment/<int:assessment_id>/paediatric_neurologist_referral_date",
        paediatric_neurologist_referral_date,
        name="paediatric_neurologist_referral_date",
    ),
    path(
        "assessment/<int:assessment_id>/paediatric_neurologist_input_date",
        paediatric_neurologist_input_date,
        name="paediatric_neurologist_input_date",
    ),
    #     paediatric neurology centre selection
    path(
        "assessment/<int:assessment_id>/paediatric_neurology_centre",
        paediatric_neurology_centre,
        name="paediatric_neurology_centre",
    ),
    path(
        "assessment/<int:assessment_id>/paediatric_neurology_centre/<int:site_id>/delete",
        delete_paediatric_neurology_centre,
        name="delete_paediatric_neurology_centre",
    ),
    path(
        "assessment/<int:assessment_id>/paediatric_neurology_centre/<int:site_id>/edit",
        edit_paediatric_neurology_centre,
        name="edit_paediatric_neurology_centre",
    ),
    path(
        "assessment/<int:assessment_id>/paediatric_neurology_centre/<int:site_id>/active/<str:action>",
        update_paediatric_neurology_centre_pressed,
        name="update_paediatric_neurology_centre_pressed",
    ),
    #     Epilepsy nurse specialist fields
    path(
        "assessment/<int:assessment_id>/epilepsy_specialist_nurse_referral_made",
        epilepsy_specialist_nurse_referral_made,
        name="epilepsy_specialist_nurse_referral_made",
    ),
    path(
        "assessment/<int:assessment_id>/epilepsy_specialist_nurse_referral_date",
        epilepsy_specialist_nurse_referral_date,
        name="epilepsy_specialist_nurse_referral_date",
    ),
    path(
        "assessment/<int:assessment_id>/epilepsy_specialist_nurse_input_date",
        epilepsy_specialist_nurse_input_date,
        name="epilepsy_specialist_nurse_input_date",
    ),
    #     Children's epilepsy surgery fields
    path(
        "assessment/<int:assessment_id>/childrens_epilepsy_surgical_service_referral_criteria_met",
        childrens_epilepsy_surgical_service_referral_criteria_met,
        name="childrens_epilepsy_surgical_service_referral_criteria_met",
    ),
    path(
        "assessment/<int:assessment_id>/childrens_epilepsy_surgical_service_referral_made",
        childrens_epilepsy_surgical_service_referral_made,
        name="childrens_epilepsy_surgical_service_referral_made",
    ),
    path(
        "assessment/<int:assessment_id>/childrens_epilepsy_surgical_service_referral_date",
        childrens_epilepsy_surgical_service_referral_date,
        name="childrens_epilepsy_surgical_service_referral_date",
    ),
    path(
        "assessment/<int:assessment_id>/childrens_epilepsy_surgical_service_review_date_status/<str:status>",
        childrens_epilepsy_surgical_service_review_date_status,
        name="childrens_epilepsy_surgical_service_review_date_status",
    ),
    path(
        "assessment/<int:assessment_id>/childrens_epilepsy_surgical_service_input_date",
        childrens_epilepsy_surgical_service_input_date,
        name="childrens_epilepsy_surgical_service_input_date",
    ),
    # children's epilepsy surgery centre selection
    path(
        "assessment/<int:assessment_id>/epilepsy_surgery_centre",
        epilepsy_surgery_centre,
        name="epilepsy_surgery_centre",
    ),
    path(
        "assessment/<int:assessment_id>/epilepsy_surgery_centre/<int:site_id>/delete",
        delete_epilepsy_surgery_centre,
        name="delete_epilepsy_surgery_centre",
    ),
    path(
        "assessment/<int:assessment_id>/epilepsy_surgery_centre/<int:site_id>/edit",
        edit_epilepsy_surgery_centre,
        name="edit_epilepsy_surgery_centre",
    ),
    path(
        "assessment/<int:assessment_id>/epilepsy_surgery_centre/<int:site_id>/active/<str:action>",
        update_epilepsy_surgery_centre_pressed,
        name="update_epilepsy_surgery_centre_pressed",
    ),
]

multiaxial_diagnosis_patterns = [
    path(
        "multiaxial_diagnosis/<int:case_id>",
        view=multiaxial_diagnosis_views.multiaxial_diagnosis,
        name="multiaxial_diagnosis",
    ),
    path(
        "multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/mental_health_screen",
        mental_health_screen,
        name="mental_health_screen",
    ),
    path(
        "multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/mental_health_issue_identified",
        mental_health_issue_identified,
        name="mental_health_issue_identified",
    ),
    path(
        "multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/mental_health_issues",
        mental_health_issues,
        name="mental_health_issues",
    ),
    path(
        "multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/autistic_spectrum_disorder",
        autistic_spectrum_disorder,
        name="autistic_spectrum_disorder",
    ),
    path(
        "multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/global_developmental_delay_or_learning_difficulties",
        global_developmental_delay_or_learning_difficulties,
        name="global_developmental_delay_or_learning_difficulties",
    ),
    path(
        "multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/global_developmental_delay_or_learning_difficulties_severity",
        global_developmental_delay_or_learning_difficulties_severity,
        name="global_developmental_delay_or_learning_difficulties_severity",
    ),
]

epilepsy_context_patterns = [
    path(
        "epilepsy_context/<int:case_id>",
        view=epilepsy_context_views.epilepsy_context,
        name="epilepsy_context",
    ),
    path(
        "epilepsy_context/<int:epilepsy_context_id>/previous_febrile_seizure",
        previous_febrile_seizure,
        name="previous_febrile_seizure",
    ),
    path(
        "epilepsy_context/<int:epilepsy_context_id>/previous_acute_symptomatic_seizure",
        previous_acute_symptomatic_seizure,
        name="previous_acute_symptomatic_seizure",
    ),
    path(
        "epilepsy_context/<int:epilepsy_context_id>/is_there_a_family_history_of_epilepsy",
        is_there_a_family_history_of_epilepsy,
        name="is_there_a_family_history_of_epilepsy",
    ),
    path(
        "epilepsy_context/<int:epilepsy_context_id>/previous_neonatal_seizures",
        previous_neonatal_seizures,
        name="previous_neonatal_seizures",
    ),
    path(
        "epilepsy_context/<int:epilepsy_context_id>/were_any_of_the_epileptic_seizures_convulsive",
        were_any_of_the_epileptic_seizures_convulsive,
        name="were_any_of_the_epileptic_seizures_convulsive",
    ),
    path(
        "epilepsy_context/<int:epilepsy_context_id>/experienced_prolonged_generalized_convulsive_seizures",
        experienced_prolonged_generalized_convulsive_seizures,
        name="experienced_prolonged_generalized_convulsive_seizures",
    ),
    path(
        "epilepsy_context/<int:epilepsy_context_id>/experienced_prolonged_focal_seizures",
        experienced_prolonged_focal_seizures,
        name="experienced_prolonged_focal_seizures",
    ),
    path(
        "epilepsy_context/<int:epilepsy_context_id>/diagnosis_of_epilepsy_withdrawn",
        diagnosis_of_epilepsy_withdrawn,
        name="diagnosis_of_epilepsy_withdrawn",
    ),
]

management_patterns = [
    path(
        "management/<int:case_id>", view=management_views.management, name="management"
    ),
    path(
        "management/<int:management_id>/has_an_aed_been_given",
        has_an_aed_been_given,
        name="has_an_aed_been_given",
    ),
    path(
        "management/<int:management_id>/has_rescue_medication_been_prescribed",
        has_rescue_medication_been_prescribed,
        name="has_rescue_medication_been_prescribed",
    ),
    path(
        "management/<int:management_id>/individualised_care_plan_in_place",
        individualised_care_plan_in_place,
        name="individualised_care_plan_in_place",
    ),
    path(
        "management/<int:management_id>/individualised_care_plan_date",
        individualised_care_plan_date,
        name="individualised_care_plan_date",
    ),
    path(
        "management/<int:management_id>/individualised_care_plan_has_parent_carer_child_agreement",
        individualised_care_plan_has_parent_carer_child_agreement,
        name="individualised_care_plan_has_parent_carer_child_agreement",
    ),
    path(
        "management/<int:management_id>/individualised_care_plan_includes_service_contact_details",
        individualised_care_plan_includes_service_contact_details,
        name="individualised_care_plan_includes_service_contact_details",
    ),
    path(
        "management/<int:management_id>/individualised_care_plan_include_first_aid",
        individualised_care_plan_include_first_aid,
        name="individualised_care_plan_include_first_aid",
    ),
    path(
        "management/<int:management_id>/individualised_care_plan_parental_prolonged_seizure_care",
        individualised_care_plan_parental_prolonged_seizure_care,
        name="individualised_care_plan_parental_prolonged_seizure_care",
    ),
    path(
        "management/<int:management_id>/individualised_care_plan_includes_general_participation_risk",
        individualised_care_plan_includes_general_participation_risk,
        name="individualised_care_plan_includes_general_participation_risk",
    ),
    path(
        "management/<int:management_id>/individualised_care_plan_addresses_water_safety",
        individualised_care_plan_addresses_water_safety,
        name="individualised_care_plan_addresses_water_safety",
    ),
    path(
        "management/<int:management_id>/individualised_care_plan_addresses_sudep",
        individualised_care_plan_addresses_sudep,
        name="individualised_care_plan_addresses_sudep",
    ),
    path(
        "management/<int:management_id>/individualised_care_plan_includes_ehcp",
        individualised_care_plan_includes_ehcp,
        name="individualised_care_plan_includes_ehcp",
    ),
    path(
        "management/<int:management_id>/has_individualised_care_plan_been_updated_in_the_last_year",
        has_individualised_care_plan_been_updated_in_the_last_year,
        name="has_individualised_care_plan_been_updated_in_the_last_year",
    ),
    path(
        "management/<int:management_id>/has_been_referred_for_mental_health_support",
        has_been_referred_for_mental_health_support,
        name="has_been_referred_for_mental_health_support",
    ),
    path(
        "management/<int:management_id>/has_support_for_mental_health_support",
        has_support_for_mental_health_support,
        name="has_support_for_mental_health_support",
    ),
]

investigations_patterns = [
    path(
        "investigations/<int:case_id>",
        view=investigation_views.investigations,
        name="investigations",
    ),
    path(
        "investigations/<int:investigations_id>/eeg_indicated",
        eeg_indicated,
        name="eeg_indicated",
    ),
    path(
        "investigations/<int:investigations_id>/eeg_request_date",
        eeg_request_date,
        name="eeg_request_date",
    ),
    path(
        "investigations/<int:investigations_id>/eeg_performed_date",
        eeg_performed_date,
        name="eeg_performed_date",
    ),
    path(
        "investigations/<int:investigations_id>/eeg_declined/<str:confirm>",
        eeg_declined,
        name="eeg_declined",
    ),
    path(
        "investigations/<int:investigations_id>/twelve_lead_ecg_status",
        twelve_lead_ecg_status,
        name="twelve_lead_ecg_status",
    ),
    path(
        "investigations/<int:investigations_id>/ct_head_scan_status",
        ct_head_scan_status,
        name="ct_head_scan_status",
    ),
    path(
        "investigations/<int:investigations_id>/mri_indicated",
        mri_indicated,
        name="mri_indicated",
    ),
    path(
        "investigations/<int:investigations_id>/mri_brain_requested_date",
        mri_brain_requested_date,
        name="mri_brain_requested_date",
    ),
    path(
        "investigations/<int:investigations_id>/mri_brain_reported_date",
        mri_brain_reported_date,
        name="mri_brain_reported_date",
    ),
    path(
        "investigations/<int:investigations_id>/mri_brain_declined/<str:confirm>",
        mri_brain_declined,
        name="mri_brain_declined",
    ),
]

episode_patterns = [
    path(
        "multiaxial_diagnosis_id/<int:multiaxial_diagnosis_id>/add_episode",
        add_episode,
        name="add_episode",
    ),
    path("episode/<int:episode_id>/edit", edit_episode, name="edit_episode"),
    path("episode/<int:episode_id>/delete", remove_episode, name="remove_episode"),
    path("episode/<int:episode_id>/close", close_episode, name="close_episode"),
    path(
        "episode/<int:episode_id>/seizure_onset_date",
        seizure_onset_date,
        name="seizure_onset_date",
    ),
    path(
        "episode/<int:episode_id>/seizure_onset_date_confidence",
        seizure_onset_date_confidence,
        name="seizure_onset_date_confidence",
    ),
    path(
        "episode/<int:episode_id>/episode_definition",
        episode_definition,
        name="episode_definition",
    ),
    path(
        "episode/<int:episode_id>/has_description_of_the_episode_or_episodes_been_gathered",
        has_description_of_the_episode_or_episodes_been_gathered,
        name="has_description_of_the_episode_or_episodes_been_gathered",
    ),
    path(
        "episode/<int:episode_id>/description",
        edit_description,
        name="edit_description",
    ),
    path(
        "episode/<int:episode_id>/description_keyword/<int:description_keyword_id>/delete",
        delete_description_keyword,
        name="delete_description_keyword",
    ),
    path(
        "episode/<int:episode_id>/epilepsy_or_nonepilepsy_status",
        epilepsy_or_nonepilepsy_status,
        name="epilepsy_or_nonepilepsy_status",
    ),
    path(
        "episode/<int:episode_id>/epileptic_seizure_onset_type",
        epileptic_seizure_onset_type,
        name="epileptic_seizure_onset_type",
    ),
    path(
        "episode/<int:episode_id>/focal_onset_epilepsy_checked_changed",
        focal_onset_epilepsy_checked_changed,
        name="focal_onset_epilepsy_checked_changed",
    ),
    path(
        "episode/<int:episode_id>/epileptic_generalised_onset",
        epileptic_generalised_onset,
        name="epileptic_generalised_onset",
    ),
    path(
        "episode/<int:episode_id>/nonepilepsy_generalised_onset",
        nonepilepsy_generalised_onset,
        name="nonepilepsy_generalised_onset",
    ),
    path(
        "episode/<int:episode_id>/nonepileptic_seizure_type",
        nonepileptic_seizure_type,
        name="nonepileptic_seizure_type",
    ),
    path(
        "episode/<int:episode_id>/nonepileptic_seizure_subtype",
        nonepileptic_seizure_subtype,
        name="nonepileptic_seizure_subtype",
    ),
]

syndromes_patterns = [
    path(
        "multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/syndrome_present",
        syndrome_present,
        name="syndrome_present",
    ),
    path(
        "multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/add_syndrome",
        add_syndrome,
        name="add_syndrome",
    ),
    path(
        "syndrome/<int:syndrome_id>/edit_syndrome",
        edit_syndrome,
        name="edit_syndrome",
    ),
    path(
        "syndrome/<int:syndrome_id>/remove_syndrome",
        remove_syndrome,
        name="remove_syndrome",
    ),
    path(
        "syndrome/<int:syndrome_id>/close_syndrome",
        close_syndrome,
        name="close_syndrome",
    ),
    path(
        "syndrome/<int:syndrome_id>/syndrome_diagnosis_date",
        syndrome_diagnosis_date,
        name="syndrome_diagnosis_date",
    ),
    path(
        "syndrome/<int:syndrome_id>/syndrome_name",
        syndrome_name,
        name="syndrome_name",
    ),
]

epilepsy_causes_patterns = [
    path(
        "multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/epilepsy_cause_known",
        epilepsy_cause_known,
        name="epilepsy_cause_known",
    ),
    path(
        "multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/epilepsy_cause",
        epilepsy_cause,
        name="epilepsy_cause",
    ),
    path(
        "multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/epilepsy_cause_categories",
        epilepsy_cause_categories,
        name="epilepsy_cause_categories",
    ),
]

comorbidities_patterns = [
    path(
        "multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/relevant_impairments_behavioural_educational",
        relevant_impairments_behavioural_educational,
        name="relevant_impairments_behavioural_educational",
    ),
    path(
        "multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/add_comorbidity",
        add_comorbidity,
        name="add_comorbidity",
    ),
    path(
        "comorbidity/<int:comorbidity_id>/edit",
        edit_comorbidity,
        name="edit_comorbidity",
    ),
    path(
        "comorbidity/<int:comorbidity_id>/remove",
        remove_comorbidity,
        name="remove_comorbidity",
    ),
    path(
        "comorbidity/<int:comorbidity_id>/close",
        close_comorbidity,
        name="close_comorbidity",
    ),
    path(
        "comorbidity/<int:comorbidity_id>/comorbidity_diagnosis_date",
        comorbidity_diagnosis_date,
        name="comorbidity_diagnosis_date",
    ),
    path(
        "comorbidity/<int:comorbidity_id>/comorbidity_diagnosis",
        comorbidity_diagnosis,
        name="comorbidity_diagnosis",
    ),
    path(
        "multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/comorbidities",
        comorbidities,
        name="comorbidities",
    ),
]

registration_patterns = [
    path(
        "registration/<int:registration_id>/registration_status",
        registration_status,
        name="registration_status",
    ),
    path(
        "registration/<int:registration_id>/confirm_eligibility",
        confirm_eligible,
        name="confirm_eligible",
    ),
    path(
        "case/<int:case_id>/first_paediatric_assessment_date",
        first_paediatric_assessment_date,
        name="first_paediatric_assessment_date",
    ),
    path(
        "registration/<int:registration_id>/lead_site/<int:site_id>/transfer",
        transfer_lead_site,
        name="transfer_lead_site",
    ),
    path(
        "registration/<int:registration_id>/lead_site/<int:site_id>/cancel",
        cancel_lead_site,
        name="cancel_lead_site",
    ),
    path(
        "registration/<int:registration_id>/lead_site/<int:site_id>/update/<str:update>",
        update_lead_site,
        name="update_lead_site",
    ),
    path(
        "registration/<int:registration_id>/allocate_lead_site",
        allocate_lead_site,
        name="allocate_lead_site",
    ),
    path(
        "registration/<int:registration_id>/site/<int:site_id>/delete",
        delete_lead_site,
        name="delete_lead_site",
    ),
    path(
        "registration/<int:registration_id>/previous_sites",
        previous_sites,
        name="previous_sites",
    ),
]

antiepilepsy_medicine_patterns = [
    path(
        "management/<int:management_id>/add_antiepilepsy_medicine/is_rescue/<str:is_rescue_medicine>",
        add_antiepilepsy_medicine,
        name="add_antiepilepsy_medicine",
    ),
    path(
        "antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/remove_antiepilepsy_medicine",
        remove_antiepilepsy_medicine,
        name="remove_antiepilepsy_medicine",
    ),
    path(
        "antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/edit_antiepilepsy_medicine",
        edit_antiepilepsy_medicine,
        name="edit_antiepilepsy_medicine",
    ),
    path(
        "antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/close",
        close_antiepilepsy_medicine,
        name="close_antiepilepsy_medicine",
    ),
    path(
        "antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/medicine_id",
        medicine_id,
        name="medicine_id",
    ),
    path(
        "antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/antiepilepsy_medicine_start_date",
        antiepilepsy_medicine_start_date,
        name="antiepilepsy_medicine_start_date",
    ),
    path(
        "antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/antiepilepsy_medicine_add_stop_date",
        antiepilepsy_medicine_add_stop_date,
        name="antiepilepsy_medicine_add_stop_date",
    ),
    path(
        "antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/antiepilepsy_medicine_remove_stop_date",
        antiepilepsy_medicine_remove_stop_date,
        name="antiepilepsy_medicine_remove_stop_date",
    ),
    path(
        "antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/antiepilepsy_medicine_stop_date",
        antiepilepsy_medicine_stop_date,
        name="antiepilepsy_medicine_stop_date",
    ),
    path(
        "antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/antiepilepsy_medicine_risk_discussed",
        antiepilepsy_medicine_risk_discussed,
        name="antiepilepsy_medicine_risk_discussed",
    ),
    path(
        "antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/is_a_pregnancy_prevention_programme_in_place",
        is_a_pregnancy_prevention_programme_in_place,
        name="is_a_pregnancy_prevention_programme_in_place",
    ),
    path(
        "antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/has_a_valproate_annual_risk_acknowledgement_form_been_completed",
        has_a_valproate_annual_risk_acknowledgement_form_been_completed,
        name="has_a_valproate_annual_risk_acknowledgement_form_been_completed",
    ),
]


urlpatterns = []

# This is related to the DRF
# drf_routes = [
#     # rest framework paths
#     path("api/v1/", include(router.urls)),
#     # returns a Token (OAuth2 key: Token) against email and password of existing user
#     path("api/v1/api-token-auth/", obtain_auth_token, name="api_token_auth"),
#     # returns the standard Django for authentication of the DRF
#     path("api/v1/api-auth/", include(urls, namespace="rest_framework")),
# ]


urlpatterns += user_patterns
urlpatterns += redirect_patterns
urlpatterns += home_page_patterns
urlpatterns += case_patterns
urlpatterns += organisation_patterns
urlpatterns += global_htmx_trigger_patterns
urlpatterns += first_paediatric_assessment_patterns
urlpatterns += assessment_patterns
urlpatterns += multiaxial_diagnosis_patterns
urlpatterns += epilepsy_context_patterns
urlpatterns += management_patterns
urlpatterns += investigations_patterns
urlpatterns += episode_patterns
urlpatterns += syndromes_patterns
urlpatterns += epilepsy_causes_patterns
urlpatterns += comorbidities_patterns
urlpatterns += registration_patterns
urlpatterns += antiepilepsy_medicine_patterns

# This is related to the DRF
# urlpatterns += drf_routes
