from . import views
from .view_folder import HospitalAutocomplete
from .view_folder import SemiologyKeywordAutocomplete
from .views import SignUpView
from django.urls import path

urlpatterns = [
    path('', views.index, name="index"),
    path('database', views.database, name="database"),
    path('tsandcs', views.tsandcs, name="tsandcs"),
    path('hospital', views.hospital_reports, name="hospital_reports"),
    path('cases/', views.case_list, name="cases"),
    path('case/<int:id>/update', views.update_case, name="update_case"),
    path('case/create', views.create_case, name="create_case"),
    path('case/<int:id>/delete', views.delete_case, name="delete_case"),
    path('case/<int:id>/register',
         views.register, name='register'),

    # initial assessment path
    path('initial_assessment/<int:case_id>',
         views.initial_assessment, name="initial_assessment"),
    # assessment path
    path('assessment/<int:case_id>/',
         views.assessment, name="assessment"),

    # multiaxial description path
    path('multiaxial_description/<int:case_id>',
         views.multiaxial_description, name='multiaxial_description'),

    # epilepsy context path
    path('epilepsy_context/<int:case_id>',
         views.epilepsy_context, name='epilepsy_context'),

    #   comorbidity paths
    path('comorbidity/<int:case_id>/create',
         views.create_comorbidity, name="create_comorbidity"),
    path('comorbidity/<int:case_id>/update',
         views.update_comorbidity, name="update_comorbidity"),
    path('management/<int:case_id>', views.management, name='management'),

    path('docs', views.documentation, name="docs"),
    path('patient', views.patient, name="patient"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path('hospital-autocomplete/', HospitalAutocomplete.as_view(),
         name='hospital-autocomplete'),
    path('semiology-keyword-autocomplete/', SemiologyKeywordAutocomplete.as_view(),
         name='semiology-keyword-autocomplete'),
    path('investigations/<int:case_id>',
         views.investigations, name='investigations')
]

htmx_paths = [
    # generic paths
    path('htmx/hospital_list',
         views.hospital_list, name='hospital_list'),


    # desscribe / multiaxial description htmx endpoints
    path('htmx/<int:desscribe_id>/description',
         views.edit_description, name='edit_description'),
    path('htmx/<int:desscribe_id>/description_keyword/<int:description_keyword_id>/delete',
         views.delete_description_keyword, name='delete_description_keyword'),
    path('htmx/<int:desscribe_id>/epilepsy_or_nonepilepsy_status',
         views.epilepsy_or_nonepilepsy_status, name='epilepsy_or_nonepilepsy_status'),
    path('htmx/<int:desscribe_id>/epileptic_seizure_onset_type',
         views.epileptic_seizure_onset_type, name='epileptic_seizure_onset_type'),
    path('htmx/<int:desscribe_id>/focal_onset_epilepsy_checked_changed',
         views.focal_onset_epilepsy_checked_changed, name='focal_onset_epilepsy_checked_changed'),
    path('htmx/desscribe/<int:desscribe_id>/experienced_prolonged_focal_seizures',
         views.experienced_prolonged_focal_seizures, name="experienced_prolonged_focal_seizures"),
    path('htmx/desscribe/<int:desscribe_id>/were_any_of_the_epileptic_seizures_convulsive',
         views.were_any_of_the_epileptic_seizures_convulsive, name="were_any_of_the_epileptic_seizures_convulsive"),
    path('htmx/desscribe/<int:desscribe_id>/prolonged_generalized_convulsive_seizures',
         views.prolonged_generalized_convulsive_seizures, name="prolonged_generalized_convulsive_seizures"),

    #     nonepilepsy
    path('htmx/<int:desscribe_id>/nonepilepsy_generalised_onset',
         views.nonepilepsy_generalised_onset, name='nonepilepsy_generalised_onset'),
    path('htmx/<int:desscribe_id>/nonepileptic_seizure_type',
         views.nonepileptic_seizure_type, name='nonepileptic_seizure_type'),
    path('htmx/<int:desscribe_id>/nonepileptic_seizure_subtype',
         views.nonepileptic_seizure_subtype, name='nonepileptic_seizure_subtype'),

    path('htmx/<int:desscribe_id>/seizure_cause_main',
         views.seizure_cause_main, name='seizure_cause_main'),
    path('htmx/<int:desscribe_id>/seizure_cause_subtype/<str:subtype>',
         views.seizure_cause_subtype, name='seizure_cause_subtype'),
    path('htmx/<int:desscribe_id>/seizure_cause_subtype_subtype',
         views.seizure_cause_subtype_subtype, name='seizure_cause_subtype_subtype'),

    # syndrome
    path('htmx/<int:desscribe_id>/syndrome_present',
         views.syndrome_present, name='syndrome_present'),
    path('htmx/<int:desscribe_id>/syndrome',
         views.syndrome, name='syndrome'),

    path('htmx/<int:desscribe_id>/ribe',
         views.ribe, name='ribe'),
    # case table endpoints
    path('htmx/filter_case_list', views.case_list,
         name="filter_case_list"),
    path('htmx/sort_by_imd_up', views.case_list,
         name="sort_by_imd_up"),
    path('htmx/sort_by_imd_down', views.case_list,
         name="sort_by_imd_down"),
    path('htmx/sort_by_nhs_number_up', views.case_list,
         name="sort_by_nhs_number_up"),
    path('htmx/sort_by_nhs_number_down', views.case_list,
         name="sort_by_nhs_number_down"),
    path('htmx/sort_by_ethnicity_up', views.case_list,
         name="sort_by_ethnicity_up"),
    path('htmx/sort_by_ethnicity_down', views.case_list,
         name="sort_by_ethnicity_down"),
    path('htmx/sort_by_gender_up', views.case_list,
         name="sort_by_gender_up"),
    path('htmx/sort_by_gender_down', views.case_list,
         name="sort_by_gender_down"),
    path('htmx/sort_by_name_up', views.case_list,
         name="sort_by_name_up"),
    path('htmx/sort_by_name_down', views.case_list,
         name="sort_by_name_down"),
    path('htmx/sort_by_id_up', views.case_list,
         name="sort_by_id_up"),
    path('htmx/sort_by_id_down', views.case_list,
         name="sort_by_id_down"),
    path('htmx/comorbidity_search',
         views.comorbidity_search, name="comorbidity_search"),
    #     registration endpoints
    path('htmx/registration<int:registration_id>/confirm_eligibility',
         views.confirm_eligible, name="confirm_eligible"),
    path('htmx/case/<int:case_id>/registration_date',
         views.registration_date, name="registration_date"),
    #     path('htmx/registration/<int:registration_id>/lead_centre',
    #          views.lead_centre, name="lead_centre"),
    path('htmx/registration/<int:registration_id>/hospital_trust_select',
         views.hospital_trust_select, name="hospital_trust_select"),

    path('htmx/registration/<int:registration_id>/lead_site/<int:site_id>/edit',
         views.edit_lead_site, name="edit_lead_site"),
    path('htmx/registration/<int:registration_id>/lead_site/<int:site_id>/transfer',
         views.transfer_lead_site, name="transfer_lead_site"),
    path('htmx/registration/<int:registration_id>/lead_site/<int:site_id>/cancel',
         views.cancel_lead_site, name="cancel_lead_site"),
    path('htmx/registration/<int:registration_id>/lead_site/<int:site_id>/update/<str:update>',
         views.update_lead_site, name="update_lead_site"),
    path('htmx/registration/<int:registration_id>/allocate_lead_site',
         views.allocate_lead_site, name="allocate_lead_site"),
    path('htmx/registration/<int:registration_id>/previous_sites',
         views.previous_sites, name="previous_sites"),


    #     ** Assessment paths **

    #     Consultant paediatrician fields
    path('htmx/assessment/<int:assessment_id>/consultant_paediatrician_referral_made',
         views.consultant_paediatrician_referral_made, name="consultant_paediatrician_referral_made"),
    path('htmx/assessment/<int:assessment_id>/consultant_paediatrician_referral_date',
         views.consultant_paediatrician_referral_date, name="consultant_paediatrician_referral_date"),
    path('htmx/assessment/<int:assessment_id>/consultant_paediatrician_input_date',
         views.consultant_paediatrician_input_date, name="consultant_paediatrician_input_date"),
    # general paediatric centre fields
    path('htmx/assessment/<int:assessment_id>/general_paediatric_centre',
         views.general_paediatric_centre, name="general_paediatric_centre"),
    path('htmx/assessment/<int:assessment_id>/general_paediatric_centre/<int:site_id>/delete',
         views.delete_general_paediatric_centre, name="delete_general_paediatric_centre"),
    path('htmx/assessment/<int:assessment_id>/general_paediatric_centre/<int:site_id>/edit',
         views.edit_general_paediatric_centre, name="edit_general_paediatric_centre"),
    path('htmx/assessment/<int:assessment_id>/general_paediatric_centre/<int:site_id>/active/<str:action>',
         views.update_general_paediatric_centre_pressed, name="update_general_paediatric_centre_pressed"),


    #     Consultant paediatric neurologist fields
    path('htmx/assessment/<int:assessment_id>/paediatric_neurologist_referral_made',
         views.paediatric_neurologist_referral_made, name="paediatric_neurologist_referral_made"),
    path('htmx/assessment/<int:assessment_id>/paediatric_neurologist_referral_date',
         views.paediatric_neurologist_referral_date, name="paediatric_neurologist_referral_date"),
    path('htmx/assessment/<int:assessment_id>/paediatric_neurologist_input_date',
         views.paediatric_neurologist_input_date, name="paediatric_neurologist_input_date"),
    #     paediatric neurology centre selection
    path('htmx/assessment/<int:assessment_id>/paediatric_neurology_centre',
         views.paediatric_neurology_centre, name="paediatric_neurology_centre"),
    path('htmx/assessment/<int:assessment_id>/paediatric_neurology_centre/<int:site_id>/delete',
         views.delete_paediatric_neurology_centre, name="delete_paediatric_neurology_centre"),
    path('htmx/assessment/<int:assessment_id>/paediatric_neurology_centre/<int:site_id>/edit',
         views.edit_paediatric_neurology_centre, name="edit_paediatric_neurology_centre"),
    path('htmx/assessment/<int:assessment_id>/paediatric_neurology_centre/<int:site_id>/active/<str:action>',
         views.update_paediatric_neurology_centre_pressed, name="update_paediatric_neurology_centre_pressed"),

    #     Epilepsy nurse specialist fields
    path('htmx/assessment/<int:assessment_id>/epilepsy_specialist_nurse_referral_made',
         views.epilepsy_specialist_nurse_referral_made, name="epilepsy_specialist_nurse_referral_made"),
    path('htmx/assessment/<int:assessment_id>/epilepsy_specialist_nurse_referral_date',
         views.epilepsy_specialist_nurse_referral_date, name="epilepsy_specialist_nurse_referral_date"),
    path('htmx/assessment/<int:assessment_id>/epilepsy_specialist_nurse_input_date',
         views.epilepsy_specialist_nurse_input_date, name="epilepsy_specialist_nurse_input_date"),

    #     Children's epilepsy surgery fields
    path('htmx/assessment/<int:assessment_id>/childrens_epilepsy_surgical_service_referral_criteria_met',
         views.childrens_epilepsy_surgical_service_referral_criteria_met, name="childrens_epilepsy_surgical_service_referral_criteria_met"),
    path('htmx/assessment/<int:assessment_id>/childrens_epilepsy_surgical_service_referral_made',
         views.childrens_epilepsy_surgical_service_referral_made, name="childrens_epilepsy_surgical_service_referral_made"),
    path('htmx/assessment/<int:assessment_id>/childrens_epilepsy_surgical_service_referral_date',
         views.childrens_epilepsy_surgical_service_referral_date, name="childrens_epilepsy_surgical_service_referral_date"),
    path('htmx/assessment/<int:assessment_id>/childrens_epilepsy_surgical_service_input_date',
         views.childrens_epilepsy_surgical_service_input_date, name="childrens_epilepsy_surgical_service_input_date"),
    # children's epilepsy surgery centre selection
    path('htmx/assessment/<int:assessment_id>/epilepsy_surgery_centre',
         views.epilepsy_surgery_centre, name="epilepsy_surgery_centre"),
    path('htmx/assessment/<int:assessment_id>/epilepsy_surgery_centre/<int:site_id>/delete',
         views.delete_epilepsy_surgery_centre, name="delete_epilepsy_surgery_centre"),
    path('htmx/assessment/<int:assessment_id>/epilepsy_surgery_centre/<int:site_id>/edit',
         views.edit_epilepsy_surgery_centre, name="edit_epilepsy_surgery_centre"),
    path('htmx/assessment/<int:assessment_id>/epilepsy_surgery_centre/<int:site_id>/active/<str:action>',
         views.update_epilepsy_surgery_centre_pressed, name="update_epilepsy_surgery_centre_pressed"),



    path('htmx/registration/<int:registration_id>/registration_status',
         views.registration_status, name="registration_status"),

    # initial assessment endpoints
    path('htmx/registration/<int:initial_assessment_id>/date_of_initial_assessment',
         views.date_of_initial_assessment, name="date_of_initial_assessment"),
    path('htmx/registration/<int:initial_assessment_id>/first_paediatric_assessment_in_acute_or_nonacute_setting',
         views.first_paediatric_assessment_in_acute_or_nonacute_setting, name="first_paediatric_assessment_in_acute_or_nonacute_setting"),
    path('htmx/registration/<int:initial_assessment_id>/general_paediatrics_referral_made',
         views.general_paediatrics_referral_made, name="general_paediatrics_referral_made"),
    path('htmx/initial_assessment/<int:initial_assessment_id>/date_of_referral_to_general_paediatrics',
         views.date_of_referral_to_general_paediatrics, name="date_of_referral_to_general_paediatrics"),
    path('htmx/registration/<int:initial_assessment_id>/when_the_first_epileptic_episode_occurred',
         views.when_the_first_epileptic_episode_occurred, name="when_the_first_epileptic_episode_occurred"),
    path('htmx/registration/<int:initial_assessment_id>/when_the_first_epileptic_episode_occurred_confidence',
         views.when_the_first_epileptic_episode_occurred_confidence, name="when_the_first_epileptic_episode_occurred_confidence"),
    path('htmx/registration/<int:initial_assessment_id>/has_description_of_the_episode_or_episodes_been_gathered',
         views.has_description_of_the_episode_or_episodes_been_gathered, name="has_description_of_the_episode_or_episodes_been_gathered"),
    path('htmx/registration/<int:initial_assessment_id>/has_number_of_episodes_since_the_first_been_documented',
         views.has_number_of_episodes_since_the_first_been_documented, name="has_number_of_episodes_since_the_first_been_documented"),
    path('htmx/registration/<int:initial_assessment_id>/general_examination_performed',
         views.general_examination_performed, name="general_examination_performed"),
    path('htmx/registration/<int:initial_assessment_id>/neurological_examination_performed',
         views.neurological_examination_performed, name="neurological_examination_performed"),
    path('htmx/registration/<int:initial_assessment_id>/developmental_learning_or_schooling_problems',
         views.developmental_learning_or_schooling_problems, name="developmental_learning_or_schooling_problems"),
    path('htmx/registration/<int:initial_assessment_id>/behavioural_or_emotional_problems',
         views.behavioural_or_emotional_problems, name="behavioural_or_emotional_problems"),
    path('htmx/registration/<int:initial_assessment_id>/diagnostic_status',
         views.diagnostic_status, name="diagnostic_status"),
    path('htmx/registration/<int:initial_assessment_id>/episode_definition',
         views.episode_definition, name="episode_definition"),

    # epilepsy context htmx
    path('htmx/epilepsy_context/<int:epilepsy_context_id>/previous_febrile_seizure',
         views.previous_febrile_seizure, name="previous_febrile_seizure"),
    path('htmx/epilepsy_context/<int:epilepsy_context_id>/previous_acute_symptomatic_seizure',
         views.previous_acute_symptomatic_seizure, name="previous_acute_symptomatic_seizure"),
    path('htmx/epilepsy_context/<int:epilepsy_context_id>/is_there_a_family_history_of_epilepsy',
         views.is_there_a_family_history_of_epilepsy, name="is_there_a_family_history_of_epilepsy"),
    path('htmx/epilepsy_context/<int:epilepsy_context_id>/previous_neonatal_seizures',
         views.previous_neonatal_seizures, name="previous_neonatal_seizures"),
    path('htmx/epilepsy_context/<int:epilepsy_context_id>/diagnosis_of_epilepsy_withdrawn',
         views.diagnosis_of_epilepsy_withdrawn, name="diagnosis_of_epilepsy_withdrawn"),

    # investigations
    path('htmx/investigations/<int:investigations_id>/eeg_indicated',
         views.eeg_indicated, name="eeg_indicated"),
    path('htmx/investigations/<int:investigations_id>/eeg_request_date',
         views.eeg_request_date, name="eeg_request_date"),
    path('htmx/investigations/<int:investigations_id>/eeg_performed_date',
         views.eeg_performed_date, name="eeg_performed_date"),

    path('htmx/investigations/<int:investigations_id>/twelve_lead_ecg_status',
         views.twelve_lead_ecg_status, name="twelve_lead_ecg_status"),
    path('htmx/investigations/<int:investigations_id>/ct_head_scan_status',
         views.ct_head_scan_status, name="ct_head_scan_status"),
    path('htmx/investigations/<int:investigations_id>/mri_indicated',
         views.mri_indicated, name="mri_indicated"),
    path('htmx/investigations/<int:investigations_id>/mri_brain_date',
         views.mri_brain_date, name="mri_brain_date"),

    # management
    path('htmx/management/<int:management_id>/has_an_aed_been_given',
         views.has_an_aed_been_given, name="has_an_aed_been_given"),
    path('htmx/management/<int:management_id>/rescue_medication_prescribed',
         views.rescue_medication_prescribed, name="rescue_medication_prescribed"),
    path('htmx/management/<int:management_id>/antiepilepsy_medicine_search',
         views.antiepilepsy_medicine_search, name='antiepilepsy_medicine_search'),
    path('htmx/management/<int:management_id>/save_selected_antiepilepsy_medicine',
         views.save_selected_antiepilepsy_medicine, name='save_selected_antiepilepsy_medicine'),
    path('htmx/management/<int:management_id>/rescue_medicine_search',
         views.rescue_medicine_search, name='rescue_medicine_search'),
    path('htmx/management/<int:management_id>/save_selected_rescue_medicine',
         views.save_selected_rescue_medicine, name='save_selected_rescue_medicine'),

    path('htmx/management/<int:management_id>/is_a_pregnancy_prevention_programme_in_place',
         views.is_a_pregnancy_prevention_programme_in_place, name='is_a_pregnancy_prevention_programme_in_place'),

    path('htmx/management/<int:management_id>/individualised_care_plan_in_place',
         views.individualised_care_plan_in_place, name='individualised_care_plan_in_place'),
    path('htmx/management/<int:management_id>/individualised_care_plan_date',
         views.individualised_care_plan_date, name='individualised_care_plan_date'),
    path('htmx/management/<int:management_id>/individualised_care_plan_has_parent_carer_child_agreement',
         views.individualised_care_plan_has_parent_carer_child_agreement, name='individualised_care_plan_has_parent_carer_child_agreement'),
    path('htmx/management/<int:management_id>/individualised_care_plan_includes_service_contact_details',
         views.individualised_care_plan_includes_service_contact_details, name='individualised_care_plan_includes_service_contact_details'),
    path('htmx/management/<int:management_id>/individualised_care_plan_include_first_aid',
         views.individualised_care_plan_include_first_aid, name='individualised_care_plan_include_first_aid'),
    path('htmx/management/<int:management_id>/individualised_care_plan_parental_prolonged_seizure_care',
         views.individualised_care_plan_parental_prolonged_seizure_care, name='individualised_care_plan_parental_prolonged_seizure_care'),
    path('htmx/management/<int:management_id>/individualised_care_plan_includes_general_participation_risk',
         views.individualised_care_plan_includes_general_participation_risk, name='individualised_care_plan_includes_general_participation_risk'),
    path('htmx/management/<int:management_id>/individualised_care_plan_addresses_water_safety',
         views.individualised_care_plan_addresses_water_safety, name='individualised_care_plan_addresses_water_safety'),
    path('htmx/management/<int:management_id>/individualised_care_plan_addresses_sudep',
         views.individualised_care_plan_addresses_sudep, name='individualised_care_plan_addresses_sudep'),
    path('htmx/management/<int:management_id>/individualised_care_plan_includes_aihp',
         views.individualised_care_plan_includes_aihp, name='individualised_care_plan_includes_aihp'),
    path('htmx/management/<int:management_id>/individualised_care_plan_includes_ehcp',
         views.individualised_care_plan_includes_ehcp, name='individualised_care_plan_includes_ehcp'),
    path('htmx/management/<int:management_id>/has_individualised_care_plan_been_updated_in_the_last_year',
         views.has_individualised_care_plan_been_updated_in_the_last_year, name='has_individualised_care_plan_been_updated_in_the_last_year'),














]


urlpatterns += htmx_paths
