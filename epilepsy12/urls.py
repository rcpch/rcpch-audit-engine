from . import views
from .view_folder import *
from django.urls import path

from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path, include
from django.contrib.auth.views import PasswordResetView

router = routers.DefaultRouter()

router.register(r'epilepsy12users', views.Epilepsy12UserViewSet)
router.register(r'registration', views.RegistrationViewSet)
router.register(r'case', views.CaseViewSet)
router.register(r'first_paediatric_assessments',
                views.FirstPaediatricAssessmentViewSet)
router.register(r'epilepsycontext', views.EpilepsyContextViewSet)
router.register(r'multiaxialdiagnosis', views.MultiaxialDiagnosisViewSet)
router.register(r'episode', views.EpisodeViewSet)
router.register(r'syndrome', views.SyndromeViewSet)
router.register(r'comorbidity', views.ComorbidityViewSet)
router.register(r'assessment', views.AssessmentViewSet)
router.register(r'investigations', views.InvestigationsViewSet)
router.register(r'management', views.ManagementViewSet)
router.register(r'antiepilepsymedicine', views.AntiEpilepsyMedicineViewSet)
router.register(r'site', views.SiteViewSet)
router.register(r'organisation', views.OrganisationViewSet)
router.register(r'keyword', views.KeywordViewSet)
router.register(r'auditprogress', views.AuditProgressViewSet)

urlpatterns = [
    path('registration/', include('django.contrib.auth.urls')),
    path('registration/login', views.epilepsy12_login, name='login'),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path("favicon", views.favicon),
    path('403', views.redirect_403, name='redirect_403'),
    path('', views.index, name="index"),
    path('database', views.database, name="database"),
    path('organisation', views.organisation_reports, name="organisation_reports"),
    path('organisation/<int:organisation_id>/cases/',
         views.case_list, name="cases"),
    path('organisation/<int:organisation_id>/case/<int:case_id>/update',
         views.update_case, name="update_case"),
    path('organisation/<int:organisation_id>/case/create',
         views.create_case, name="create_case"),
    path('organisation/<int:organisation_id>/case/unknown_postcode',
         views.unknown_postcode, name="unknown_postcode"),
    path('case/<int:case_id>/register', views.register, name='register'),
    path('case/<int:case_id>/case_performance_summary',
         views.case_performance_summary, name='case_performance_summary'),
    path('organisation/<int:organisation_id>/case/<int:case_id>/opt-out',
         views.opt_out, name='opt_out'),
    path('organisation/<int:organisation_id>/case/<int:case_id>/submit',
         views.case_submit, name='case_submit'),
    path('organisation/<int:organisation_id>/cases/view_preference/<str:template_name>',
         views.view_preference, name='view_preference'),
    path('organisation/<int:organisation_id>/cases/organisation_select/<str:template_name>',
         views.child_organisation_select, name='child_organisation_select'),
    path('organisation/<int:organisation_id>/epilepsy12_users/<int:epilepsy12_user_id>/logs',
         views.logs, name='logs'),
    path('organisation/<int:organisation_id>/epilepsy12_users/<int:epilepsy12_user_id>/log_list',
         views.log_list, name='log_list'),
    path('selected_organisation_summary', views.selected_organisation_summary,
         name='selected_organisation_summary'),
    path('selected_trust/<int:organisation_id>/kpis', views.selected_trust_kpis,
         name='selected_trust_kpis'),
    path('selected_trust_kpis/<int:organisation_id>/select_kpi', views.selected_trust_select_kpi,
         name='selected_trust_select_kpi'),
    path('organisation/<int:organisation_id>/case_statistics',
         views.case_statistics, name='case_statistics'),
    path('registration/<int:case_id>/registration_active/<str:active_template>',
         view=views.registration_active, name='registration_active'),
    path('first_paediatric_assessment/<int:case_id>/edit',
         first_paediatric_assessment, name='first_paediatric_assessment'),
    path('assessment/<int:case_id>/', assessment, name="assessment"),
    path('multiaxial_diagnosis/<int:case_id>',
         multiaxial_diagnosis, name='multiaxial_diagnosis'),
    path('epilepsy_context/<int:case_id>',
         epilepsy_context, name='epilepsy_context'),
    path('management/<int:case_id>', management, name='management'),
    path('docs', views.documentation, name="docs"),
    path('patient', views.patient, name="patient"),
    path('investigations/<int:case_id>',
         investigations, name='investigations'),
    path('organisation/<int:organisation_id>/epilepsy12_user_list/',
         views.epilepsy12_user_list, name='epilepsy12_user_list'),
    path('organisation/<int:organisation_id>/epilepsy12_users/create',
         views.create_epilepsy12_user, name='create_epilepsy12_user'),
    path('organisation/<int:organisation_id>/epilepsy12_users/<int:epilepsy12_user_id>/delete',
         views.delete_epilepsy12_user, name='delete_epilepsy12_user'),
    path('organisation/<int:organisation_id>/epilepsy12_users/<int:epilepsy12_user_id>/edit',
         views.edit_epilepsy12_user, name='edit_epilepsy12_user'),

]

htmx_paths = [
    # episodes
    path('multiaxial_diagnosis_id/<int:multiaxial_diagnosis_id>/add_episode',
         views.add_episode, name='add_episode'),
    path('episode/<int:episode_id>/edit',
         views.edit_episode, name='edit_episode'),
    path('episode/<int:episode_id>/delete',
         views.remove_episode, name='remove_episode'),
    path('episode/<int:episode_id>/close',
         views.close_episode, name='close_episode'),
    path('episode/<int:episode_id>/seizure_onset_date',
         views.seizure_onset_date, name='seizure_onset_date'),
    path('episode/<int:episode_id>/seizure_onset_date_confidence',
         views.seizure_onset_date_confidence, name='seizure_onset_date_confidence'),
    path('episode/<int:episode_id>/episode_definition',
         views.episode_definition, name='episode_definition'),
    path('episode/<int:episode_id>/has_description_of_the_episode_or_episodes_been_gathered',
         views.has_description_of_the_episode_or_episodes_been_gathered, name='has_description_of_the_episode_or_episodes_been_gathered'),
    path('episode/<int:episode_id>/description',
         views.edit_description, name='edit_description'),
    path('episode/<int:episode_id>/description_keyword/<int:description_keyword_id>/delete',
         views.delete_description_keyword, name='delete_description_keyword'),
    path('episode/<int:episode_id>/epilepsy_or_nonepilepsy_status',
         views.epilepsy_or_nonepilepsy_status, name='epilepsy_or_nonepilepsy_status'),
    path('episode/<int:episode_id>/epileptic_seizure_onset_type',
         views.epileptic_seizure_onset_type, name='epileptic_seizure_onset_type'),
    path('episode/<int:episode_id>/focal_onset_epilepsy_checked_changed',
         views.focal_onset_epilepsy_checked_changed, name='focal_onset_epilepsy_checked_changed'),
    path('episode/<int:episode_id>/epileptic_generalised_onset',
         views.epileptic_generalised_onset, name='epileptic_generalised_onset'),
    path('episode/<int:episode_id>/nonepilepsy_generalised_onset',
         views.nonepilepsy_generalised_onset, name='nonepilepsy_generalised_onset'),
    path('episode/<int:episode_id>/nonepileptic_seizure_type',
         views.nonepileptic_seizure_type, name='nonepileptic_seizure_type'),
    path('episode/<int:episode_id>/nonepileptic_seizure_subtype',
         views.nonepileptic_seizure_subtype, name='nonepileptic_seizure_subtype'),
    # epilepsy syndromes
    path('multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/syndrome_present',
         views.syndrome_present, name='syndrome_present'),
    path('multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/add_syndrome',
         views.add_syndrome, name='add_syndrome'),
    path('syndrome/<int:syndrome_id>/edit_syndrome',
         views.edit_syndrome, name='edit_syndrome'),
    path('syndrome/<int:syndrome_id>/remove_syndrome',
         views.remove_syndrome, name='remove_syndrome'),
    path('syndrome/<int:syndrome_id>/close_syndrome',
         views.close_syndrome, name='close_syndrome'),
    path('syndrome/<int:syndrome_id>/syndrome_diagnosis_date',
         views.syndrome_diagnosis_date, name='syndrome_diagnosis_date'),
    path('syndrome/<int:syndrome_id>/syndrome_name',
         views.syndrome_name, name='syndrome_name'),
    # epilepsy causes
    path('multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/epilepsy_cause_known',
         views.epilepsy_cause_known, name='epilepsy_cause_known'),
    path('multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/epilepsy_cause',
         views.epilepsy_cause, name='epilepsy_cause'),
    path('multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/epilepsy_cause_categories',
         views.epilepsy_cause_categories, name='epilepsy_cause_categories'),
    # comorbidities
    path('multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/relevant_impairments_behavioural_educational',
         views.relevant_impairments_behavioural_educational, name='relevant_impairments_behavioural_educational'),
    path('multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/add_comorbidity',
         views.add_comorbidity, name='add_comorbidity'),
    path('comorbidity/<int:comorbidity_id>/edit',
         views.edit_comorbidity, name='edit_comorbidity'),
    path('comorbidity/<int:comorbidity_id>/remove',
         views.remove_comorbidity, name='remove_comorbidity'),
    path('comorbidity/<int:comorbidity_id>/close',
         views.close_comorbidity, name='close_comorbidity'),
    path('comorbidity/<int:comorbidity_id>/comorbidity_diagnosis_date',
         views.comorbidity_diagnosis_date, name='comorbidity_diagnosis_date'),
    path('comorbidity/<int:comorbidity_id>/comorbidity_diagnosis',
         views.comorbidity_diagnosis, name='comorbidity_diagnosis'),
    path('multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/comorbidities',
         views.comorbidities, name='comorbidities'),

    path('multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/mental_health_screen',
         views.mental_health_screen, name='mental_health_screen'),
    path('multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/mental_health_issue_identified',
         views.mental_health_issue_identified, name='mental_health_issue_identified'),
    path('multiaxial_diagnosis/<int:multiaxial_diagnosis_id>/mental_health_issue',
         views.mental_health_issue, name='mental_health_issue'),

    # epilepsy12_user
    path('organisation/<int:organisation_id>/filtered_epilepsy12_user_list', views.epilepsy12_user_list,
         name="filtered_epilepsy12_user_list"),
    path('organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_name_up', views.epilepsy12_user_list,
         name="sort_epilepsy12_users_by_name_up"),
    path('organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_name_down', views.epilepsy12_user_list,
         name="sort_epilepsy12_users_by_name_down"),
    path('organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_email_up', views.epilepsy12_user_list,
         name="sort_epilepsy12_users_by_email_up"),
    path('organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_email_down', views.epilepsy12_user_list,
         name="sort_epilepsy12_users_by_email_down"),
    path('organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_role_up', views.epilepsy12_user_list,
         name="sort_epilepsy12_users_by_role_up"),
    path('organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_role_down', views.epilepsy12_user_list,
         name="sort_epilepsy12_users_by_role_down"),
    path('organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_organisation_employer_up', views.epilepsy12_user_list,
         name="sort_epilepsy12_users_by_organisation_employer_up"),
    path('organisation/<int:organisation_id>/epilepsy12_user/sort_epilepsy12_users_by_organisation_employer_down', views.epilepsy12_user_list,
         name="sort_epilepsy12_users_by_organisation_employer_down"),


    # case table endpoints
    path('htmx/filter_case_list/<organisation_id>', views.case_list,
         name="filter_case_list"),
    path('htmx/sort_by_nhs_number_up/<int:organisation_id>', views.case_list,
         name="sort_by_nhs_number_up"),
    path('htmx/sort_by_nhs_number_down/<int:organisation_id>', views.case_list,
         name="sort_by_nhs_number_down"),
    path('htmx/sort_by_sex_up/<int:organisation_id>', views.case_list,
         name="sort_by_sex_up"),
    path('htmx/sort_by_sex_down/<int:organisation_id>', views.case_list,
         name="sort_by_sex_down"),
    path('htmx/sort_by_name_up/<int:organisation_id>', views.case_list,
         name="sort_by_name_up"),
    path('htmx/sort_by_name_down/<int:organisation_id>', views.case_list,
         name="sort_by_name_down"),
    path('htmx/sort_by_id_up/<int:organisation_id>', views.case_list,
         name="sort_by_id_up"),
    path('htmx/sort_by_id_down/<int:organisation_id>', views.case_list,
         name="sort_by_id_down"),
    path('htmx/sort_by_deadline_up/<int:organisation_id>', views.case_list,
         name="sort_by_deadline_up"),
    path('htmx/sort_by_deadline_down/<int:organisation_id>', views.case_list,
         name="sort_by_deadline_down"),
    path('htmx/sort_by_cohort_up/<int:organisation_id>', views.case_list,
         name="sort_by_cohort_up"),
    path('htmx/sort_by_cohort_down/<int:organisation_id>', views.case_list,
         name="sort_by_cohort_down"),
    path('htmx/sort_by_days_remaining_before_submission_up/<int:organisation_id>', views.case_list,
         name="sort_by_days_remaining_before_submission_up"),
    path('htmx/sort_by_days_remaining_before_submission_down/<int:organisation_id>', views.case_list,
         name="sort_by_days_remaining_before_submission_down"),

    #     registration endpoints
    path('registration/<int:registration_id>/confirm_eligibility',
         views.confirm_eligible, name="confirm_eligible"),
    path('case/<int:case_id>/registration_date',
         views.registration_date, name="registration_date"),
    path('registration/<int:registration_id>/lead_site/<int:site_id>/edit',
         views.edit_lead_site, name="edit_lead_site"),
    path('registration/<int:registration_id>/lead_site/<int:site_id>/transfer',
         views.transfer_lead_site, name="transfer_lead_site"),
    path('registration/<int:registration_id>/lead_site/<int:site_id>/cancel',
         views.cancel_lead_site, name="cancel_lead_site"),
    path('registration/<int:registration_id>/lead_site/<int:site_id>/update/<str:update>',
         views.update_lead_site, name="update_lead_site"),
    path('registration/<int:registration_id>/allocate_lead_site',
         views.allocate_lead_site, name="allocate_lead_site"),
    path('registration/<int:registration_id>/site/<int:site_id>/delete',
         views.delete_lead_site, name="delete_lead_site"),
    path('registration/<int:registration_id>/previous_sites',
         views.previous_sites, name="previous_sites"),

    #     ** Assessment paths **

    #     Consultant paediatrician fields
    path('assessment/<int:assessment_id>/consultant_paediatrician_referral_made',
         views.consultant_paediatrician_referral_made, name="consultant_paediatrician_referral_made"),
    path('assessment/<int:assessment_id>/consultant_paediatrician_referral_date',
         views.consultant_paediatrician_referral_date, name="consultant_paediatrician_referral_date"),
    path('assessment/<int:assessment_id>/consultant_paediatrician_input_date',
         views.consultant_paediatrician_input_date, name="consultant_paediatrician_input_date"),
    # general paediatric centre fields
    path('assessment/<int:assessment_id>/general_paediatric_centre',
         views.general_paediatric_centre, name="general_paediatric_centre"),
    path('assessment/<int:assessment_id>/general_paediatric_centre/<int:site_id>/delete',
         views.delete_general_paediatric_centre, name="delete_general_paediatric_centre"),
    path('assessment/<int:assessment_id>/general_paediatric_centre/<int:site_id>/edit',
         views.edit_general_paediatric_centre, name="edit_general_paediatric_centre"),
    path('assessment/<int:assessment_id>/general_paediatric_centre/<int:site_id>/active/<str:action>',
         views.update_general_paediatric_centre_pressed, name="update_general_paediatric_centre_pressed"),


    #     Consultant paediatric neurologist fields
    path('assessment/<int:assessment_id>/paediatric_neurologist_referral_made',
         views.paediatric_neurologist_referral_made, name="paediatric_neurologist_referral_made"),
    path('assessment/<int:assessment_id>/paediatric_neurologist_referral_date',
         views.paediatric_neurologist_referral_date, name="paediatric_neurologist_referral_date"),
    path('assessment/<int:assessment_id>/paediatric_neurologist_input_date',
         views.paediatric_neurologist_input_date, name="paediatric_neurologist_input_date"),
    #     paediatric neurology centre selection
    path('assessment/<int:assessment_id>/paediatric_neurology_centre',
         views.paediatric_neurology_centre, name="paediatric_neurology_centre"),
    path('assessment/<int:assessment_id>/paediatric_neurology_centre/<int:site_id>/delete',
         views.delete_paediatric_neurology_centre, name="delete_paediatric_neurology_centre"),
    path('assessment/<int:assessment_id>/paediatric_neurology_centre/<int:site_id>/edit',
         views.edit_paediatric_neurology_centre, name="edit_paediatric_neurology_centre"),
    path('assessment/<int:assessment_id>/paediatric_neurology_centre/<int:site_id>/active/<str:action>',
         views.update_paediatric_neurology_centre_pressed, name="update_paediatric_neurology_centre_pressed"),

    #     Epilepsy nurse specialist fields
    path('assessment/<int:assessment_id>/epilepsy_specialist_nurse_referral_made',
         views.epilepsy_specialist_nurse_referral_made, name="epilepsy_specialist_nurse_referral_made"),
    path('assessment/<int:assessment_id>/epilepsy_specialist_nurse_referral_date',
         views.epilepsy_specialist_nurse_referral_date, name="epilepsy_specialist_nurse_referral_date"),
    path('assessment/<int:assessment_id>/epilepsy_specialist_nurse_input_date',
         views.epilepsy_specialist_nurse_input_date, name="epilepsy_specialist_nurse_input_date"),

    #     Children's epilepsy surgery fields
    path('assessment/<int:assessment_id>/childrens_epilepsy_surgical_service_referral_criteria_met',
         views.childrens_epilepsy_surgical_service_referral_criteria_met, name="childrens_epilepsy_surgical_service_referral_criteria_met"),
    path('assessment/<int:assessment_id>/childrens_epilepsy_surgical_service_referral_made',
         views.childrens_epilepsy_surgical_service_referral_made, name="childrens_epilepsy_surgical_service_referral_made"),
    path('assessment/<int:assessment_id>/childrens_epilepsy_surgical_service_referral_date',
         views.childrens_epilepsy_surgical_service_referral_date, name="childrens_epilepsy_surgical_service_referral_date"),
    path('assessment/<int:assessment_id>/childrens_epilepsy_surgical_service_input_date',
         views.childrens_epilepsy_surgical_service_input_date, name="childrens_epilepsy_surgical_service_input_date"),
    # children's epilepsy surgery centre selection
    path('assessment/<int:assessment_id>/epilepsy_surgery_centre',
         views.epilepsy_surgery_centre, name="epilepsy_surgery_centre"),
    path('assessment/<int:assessment_id>/epilepsy_surgery_centre/<int:site_id>/delete',
         views.delete_epilepsy_surgery_centre, name="delete_epilepsy_surgery_centre"),
    path('assessment/<int:assessment_id>/epilepsy_surgery_centre/<int:site_id>/edit',
         views.edit_epilepsy_surgery_centre, name="edit_epilepsy_surgery_centre"),
    path('assessment/<int:assessment_id>/epilepsy_surgery_centre/<int:site_id>/active/<str:action>',
         views.update_epilepsy_surgery_centre_pressed, name="update_epilepsy_surgery_centre_pressed"),


    path('registration/<int:registration_id>/registration_status',
         views.registration_status, name="registration_status"),

    # initial assessment endpoints

    path('registration/<int:first_paediatric_assessment_id>/first_paediatric_assessment_in_acute_or_nonacute_setting',
         views.first_paediatric_assessment_in_acute_or_nonacute_setting, name="first_paediatric_assessment_in_acute_or_nonacute_setting"),

    path('registration/<int:first_paediatric_assessment_id>/has_number_of_episodes_since_the_first_been_documented',
         views.has_number_of_episodes_since_the_first_been_documented, name="has_number_of_episodes_since_the_first_been_documented"),
    path('registration/<int:first_paediatric_assessment_id>/general_examination_performed',
         views.general_examination_performed, name="general_examination_performed"),
    path('registration/<int:first_paediatric_assessment_id>/neurological_examination_performed',
         views.neurological_examination_performed, name="neurological_examination_performed"),
    path('registration/<int:first_paediatric_assessment_id>/developmental_learning_or_schooling_problems',
         views.developmental_learning_or_schooling_problems, name="developmental_learning_or_schooling_problems"),
    path('registration/<int:first_paediatric_assessment_id>/behavioural_or_emotional_problems',
         views.behavioural_or_emotional_problems, name="behavioural_or_emotional_problems"),

    # epilepsy context htmx
    path('epilepsy_context/<int:epilepsy_context_id>/previous_febrile_seizure',
         views.previous_febrile_seizure, name="previous_febrile_seizure"),
    path('epilepsy_context/<int:epilepsy_context_id>/previous_acute_symptomatic_seizure',
         views.previous_acute_symptomatic_seizure, name="previous_acute_symptomatic_seizure"),
    path('epilepsy_context/<int:epilepsy_context_id>/is_there_a_family_history_of_epilepsy',
         views.is_there_a_family_history_of_epilepsy, name="is_there_a_family_history_of_epilepsy"),
    path('epilepsy_context/<int:epilepsy_context_id>/previous_neonatal_seizures',
         views.previous_neonatal_seizures, name="previous_neonatal_seizures"),
    path('epilepsy_context/<int:epilepsy_context_id>/were_any_of_the_epileptic_seizures_convulsive',
         views.were_any_of_the_epileptic_seizures_convulsive, name="were_any_of_the_epileptic_seizures_convulsive"),
    path('epilepsy_context/<int:epilepsy_context_id>/experienced_prolonged_generalized_convulsive_seizures',
         views.experienced_prolonged_generalized_convulsive_seizures, name="experienced_prolonged_generalized_convulsive_seizures"),
    path('epilepsy_context/<int:epilepsy_context_id>/experienced_prolonged_focal_seizures',
         views.experienced_prolonged_focal_seizures, name="experienced_prolonged_focal_seizures"),
    path('epilepsy_context/<int:epilepsy_context_id>/diagnosis_of_epilepsy_withdrawn',
         views.diagnosis_of_epilepsy_withdrawn, name="diagnosis_of_epilepsy_withdrawn"),

    # investigations
    path('investigations/<int:investigations_id>/eeg_indicated',
         views.eeg_indicated, name="eeg_indicated"),
    path('investigations/<int:investigations_id>/eeg_request_date',
         views.eeg_request_date, name="eeg_request_date"),
    path('investigations/<int:investigations_id>/eeg_performed_date',
         views.eeg_performed_date, name="eeg_performed_date"),

    path('investigations/<int:investigations_id>/twelve_lead_ecg_status',
         views.twelve_lead_ecg_status, name="twelve_lead_ecg_status"),
    path('investigations/<int:investigations_id>/ct_head_scan_status',
         views.ct_head_scan_status, name="ct_head_scan_status"),
    path('investigations/<int:investigations_id>/mri_indicated',
         views.mri_indicated, name="mri_indicated"),
    path('investigations/<int:investigations_id>/mri_brain_requested_date',
         views.mri_brain_requested_date, name="mri_brain_requested_date"),
    path('investigations/<int:investigations_id>/mri_brain_reported_date',
         views.mri_brain_reported_date, name="mri_brain_reported_date"),

    # management
    path('management/<int:management_id>/has_an_aed_been_given',
         views.has_an_aed_been_given, name="has_an_aed_been_given"),
    path('management/<int:management_id>/has_rescue_medication_been_prescribed',
         views.has_rescue_medication_been_prescribed, name="has_rescue_medication_been_prescribed"),

    # antiepilepsy medicines
    path('management/<int:management_id>/add_antiepilepsy_medicine/is_rescue/<str:is_rescue_medicine>',
         views.add_antiepilepsy_medicine, name='add_antiepilepsy_medicine'),
    path('antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/remove_antiepilepsy_medicine',
         views.remove_antiepilepsy_medicine, name='remove_antiepilepsy_medicine'),
    path('antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/edit_antiepilepsy_medicine',
         views.edit_antiepilepsy_medicine, name='edit_antiepilepsy_medicine'),
    path('antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/close',
         views.close_antiepilepsy_medicine, name='close_antiepilepsy_medicine'),
    path('antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/medicine_id',
         views.medicine_id, name='medicine_id'),
    path('antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/antiepilepsy_medicine_start_date',
         views.antiepilepsy_medicine_start_date, name='antiepilepsy_medicine_start_date'),
    path('antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/antiepilepsy_medicine_add_stop_date',
         views.antiepilepsy_medicine_add_stop_date, name='antiepilepsy_medicine_add_stop_date'),
    path('antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/antiepilepsy_medicine_stop_date',
         views.antiepilepsy_medicine_stop_date, name='antiepilepsy_medicine_stop_date'),
    path('antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/antiepilepsy_medicine_risk_discussed',
         views.antiepilepsy_medicine_risk_discussed, name='antiepilepsy_medicine_risk_discussed'),
    path('antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/is_a_pregnancy_prevention_programme_in_place',
         views.is_a_pregnancy_prevention_programme_in_place, name='is_a_pregnancy_prevention_programme_in_place'),
    path('antiepilepsy_medicine/<int:antiepilepsy_medicine_id>/has_a_valproate_annual_risk_acknowledgement_form_been_completed',
         views.has_a_valproate_annual_risk_acknowledgement_form_been_completed, name='has_a_valproate_annual_risk_acknowledgement_form_been_completed'),



    path('management/<int:management_id>/individualised_care_plan_in_place',
         views.individualised_care_plan_in_place, name='individualised_care_plan_in_place'),
    path('management/<int:management_id>/individualised_care_plan_date',
         views.individualised_care_plan_date, name='individualised_care_plan_date'),
    path('management/<int:management_id>/individualised_care_plan_has_parent_carer_child_agreement',
         views.individualised_care_plan_has_parent_carer_child_agreement, name='individualised_care_plan_has_parent_carer_child_agreement'),
    path('management/<int:management_id>/individualised_care_plan_includes_service_contact_details',
         views.individualised_care_plan_includes_service_contact_details, name='individualised_care_plan_includes_service_contact_details'),
    path('management/<int:management_id>/individualised_care_plan_include_first_aid',
         views.individualised_care_plan_include_first_aid, name='individualised_care_plan_include_first_aid'),
    path('management/<int:management_id>/individualised_care_plan_parental_prolonged_seizure_care',
         views.individualised_care_plan_parental_prolonged_seizure_care, name='individualised_care_plan_parental_prolonged_seizure_care'),
    path('management/<int:management_id>/individualised_care_plan_includes_general_participation_risk',
         views.individualised_care_plan_includes_general_participation_risk, name='individualised_care_plan_includes_general_participation_risk'),
    path('management/<int:management_id>/individualised_care_plan_addresses_water_safety',
         views.individualised_care_plan_addresses_water_safety, name='individualised_care_plan_addresses_water_safety'),
    path('management/<int:management_id>/individualised_care_plan_addresses_sudep',
         views.individualised_care_plan_addresses_sudep, name='individualised_care_plan_addresses_sudep'),
    path('management/<int:management_id>/individualised_care_plan_includes_ehcp',
         views.individualised_care_plan_includes_ehcp, name='individualised_care_plan_includes_ehcp'),
    path('management/<int:management_id>/has_individualised_care_plan_been_updated_in_the_last_year',
         views.has_individualised_care_plan_been_updated_in_the_last_year, name='has_individualised_care_plan_been_updated_in_the_last_year'),
    path('management/<int:management_id>/has_been_referred_for_mental_health_support',
         views.has_been_referred_for_mental_health_support, name='has_been_referred_for_mental_health_support'),
    path('management/<int:management_id>/has_support_for_mental_health_support',
         views.has_support_for_mental_health_support, name='has_support_for_mental_health_support'),

    path('download_select',
         views.download_select, name='download_select'),
    path('<str:model_name>/download',
         views.download, name='download'),

]

drf_routes = [
    # rest framework paths
    path('api/v1/', include(router.urls)),
    # returns a Token (OAuth2 key: Token) against email and password of existing user
    path('api/v1/api-token-auth/', obtain_auth_token, name='api_token_auth'),
    # returns the standard Django views for authentication of the DRF
    path('api/v1/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]


urlpatterns += htmx_paths
urlpatterns += drf_routes
