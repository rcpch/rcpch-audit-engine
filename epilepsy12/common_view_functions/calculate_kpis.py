# python imports

# django imports
from django.contrib.gis.db.models import Sum
from django.apps import apps

# E12 imports
from ..general_functions import has_all_attributes
from .calculate_kpi_functions import (
    score_kpi_1,
    score_kpi_2,
    score_kpi_3,
    score_kpi_3b,
    score_kpi_4,
    score_kpi_5,
    score_kpi_6,
    score_kpi_7,
    score_kpi_8,
    score_kpi_9A,
    score_kpi_9Ai,
    score_kpi_9Aii,
    score_kpi_9Aiii,
    score_kpi_9B,
    score_kpi_9Bi,
    score_kpi_9Bii,
    score_kpi_9Biii,
    score_kpi_9Biv,
    score_kpi_9Bv,
    score_kpi_9Bvi,
    score_kpi_10,
    calculate_age_at_first_paediatric_assessment_in_years,
    check_is_registered,
)

# from epilepsy12.models import KPI
from epilepsy12.constants import KPI_SCORE


def calculate_kpis(registration_instance):
    """
    Function called on update of every field
    Identifies completed KPIs for a given registered child and passes these back to update the KPI model
    It accepts the registration instance and is called each time a related model is updated
    The outcome of a measure follows 4 potential states:
    0 - measure failed
    1 - measure achieved
    2 - measure not applicable (eg ECG in nonconvulsive seizure)
    None - measure not scored yet
    """

    KPI = apps.get_model("epilepsy12", "KPI")

    # first set default value 'NOT_SCORED' to all KPIs
    paediatrician_with_expertise_in_epilepsies = KPI_SCORE["NOT_SCORED"]
    epilepsy_specialist_nurse = KPI_SCORE["NOT_SCORED"]
    tertiary_input = KPI_SCORE["NOT_SCORED"]
    epilepsy_surgery_referral = KPI_SCORE["NOT_SCORED"]
    ecg = KPI_SCORE["NOT_SCORED"]
    mri = KPI_SCORE["NOT_SCORED"]
    assessment_of_mental_health_issues = KPI_SCORE["NOT_SCORED"]
    mental_health_support = KPI_SCORE["NOT_SCORED"]
    sodium_valproate = KPI_SCORE["NOT_SCORED"]
    comprehensive_care_planning_agreement = KPI_SCORE["NOT_SCORED"]
    patient_held_individualised_epilepsy_document = KPI_SCORE["NOT_SCORED"]
    patient_carer_parent_agreement_to_the_care_planning = KPI_SCORE["NOT_SCORED"]
    care_planning_has_been_updated_when_necessary = KPI_SCORE["NOT_SCORED"]
    comprehensive_care_planning_content = KPI_SCORE["NOT_SCORED"]
    parental_prolonged_seizures_care_plan = KPI_SCORE["NOT_SCORED"]
    water_safety = KPI_SCORE["NOT_SCORED"]
    first_aid = KPI_SCORE["NOT_SCORED"]
    general_participation_and_risk = KPI_SCORE["NOT_SCORED"]
    service_contact_details = KPI_SCORE["NOT_SCORED"]
    sudep = KPI_SCORE["NOT_SCORED"]
    school_individual_healthcare_plan = KPI_SCORE["NOT_SCORED"]

    # important metric for calculations that follow
    age_at_first_paediatric_assessment = (
        calculate_age_at_first_paediatric_assessment_in_years(registration_instance)
    )

    # child must be registered in the audit for the KPI to be counted
    if not check_is_registered(registration_instance):
        # cannot proceed any further if registration incomplete.
        # In theory it should not be possible to get this far.
        return None

    if hasattr(registration_instance, "assessment"):
        paediatrician_with_expertise_in_epilepsies = score_kpi_1(registration_instance)

    if hasattr(registration_instance, "assessment"):
        epilepsy_specialist_nurse = score_kpi_2(registration_instance)

    if has_all_attributes(
        registration_instance, ["management", "assessment", "multiaxialdiagnosis"]
    ):
        tertiary_input = score_kpi_3(
            registration_instance, age_at_first_paediatric_assessment
        )

    if hasattr(registration_instance, "assessment"):
        epilepsy_surgery_referral = score_kpi_3b(registration_instance)

    if has_all_attributes(registration_instance, ["epilepsycontext", "investigations"]):
        ecg = score_kpi_4(registration_instance)

    if has_all_attributes(
        registration_instance, ["multiaxialdiagnosis", "investigations"]
    ):
        mri = score_kpi_5(registration_instance, age_at_first_paediatric_assessment)

    if hasattr(registration_instance, "multiaxialdiagnosis"):
        assessment_of_mental_health_issues = score_kpi_6(
            registration_instance, age_at_first_paediatric_assessment
        )

    if has_all_attributes(registration_instance, ["multiaxialdiagnosis", "management"]):
        mental_health_support = score_kpi_7(registration_instance)

    if hasattr(registration_instance, "management"):
        sodium_valproate = score_kpi_8(
            registration_instance, age_at_first_paediatric_assessment
        )

    if hasattr(registration_instance, "management"):
        comprehensive_care_planning_agreement = score_kpi_9A(registration_instance)

    if hasattr(registration_instance, "management"):
        patient_held_individualised_epilepsy_document = score_kpi_9Ai(
            registration_instance
        )

    if hasattr(registration_instance, "management"):
        patient_carer_parent_agreement_to_the_care_planning = score_kpi_9Aii(
            registration_instance
        )

    if hasattr(registration_instance, "management"):
        care_planning_has_been_updated_when_necessary = score_kpi_9Aiii(
            registration_instance
        )

    if hasattr(registration_instance, "management"):
        comprehensive_care_planning_content = score_kpi_9B(registration_instance)

    if hasattr(registration_instance, "management"):
        parental_prolonged_seizures_care_plan = score_kpi_9Bi(registration_instance)

    if hasattr(registration_instance, "management"):
        water_safety = score_kpi_9Bii(registration_instance)

    if hasattr(registration_instance, "management"):
        first_aid = score_kpi_9Biii(registration_instance)

    if hasattr(registration_instance, "management"):
        general_participation_and_risk = score_kpi_9Biv(registration_instance)

    if hasattr(registration_instance, "management"):
        service_contact_details = score_kpi_9Bv(registration_instance)

    if hasattr(registration_instance, "management"):
        sudep = score_kpi_9Bvi(registration_instance)

    if hasattr(registration_instance, "management"):
        school_individual_healthcare_plan = score_kpi_10(
            registration_instance, age_at_first_paediatric_assessment
        )

    # Store the KPIs in AuditProgress
    kpis = {
        "paediatrician_with_expertise_in_epilepsies": paediatrician_with_expertise_in_epilepsies,
        "epilepsy_specialist_nurse": epilepsy_specialist_nurse,
        "tertiary_input": tertiary_input,
        "epilepsy_surgery_referral": epilepsy_surgery_referral,
        "ecg": ecg,
        "mri": mri,
        "assessment_of_mental_health_issues": assessment_of_mental_health_issues,
        "mental_health_support": mental_health_support,
        "sodium_valproate": sodium_valproate,
        "comprehensive_care_planning_agreement": comprehensive_care_planning_agreement,
        "patient_held_individualised_epilepsy_document": patient_held_individualised_epilepsy_document,
        "patient_carer_parent_agreement_to_the_care_planning": patient_carer_parent_agreement_to_the_care_planning,
        "care_planning_has_been_updated_when_necessary": care_planning_has_been_updated_when_necessary,
        "comprehensive_care_planning_content": comprehensive_care_planning_content,
        "parental_prolonged_seizures_care_plan": parental_prolonged_seizures_care_plan,
        "water_safety": water_safety,
        "first_aid": first_aid,
        "general_participation_and_risk": general_participation_and_risk,
        "service_contact_details": service_contact_details,
        "sudep": sudep,
        "school_individual_healthcare_plan": school_individual_healthcare_plan,
    }

    KPI.objects.filter(pk=registration_instance.kpi.pk).update(**kpis)


def annotate_kpis(filtered_organisations, kpi_name="all"):
    """
    Single function to rationalize all functions calculatirng KPIs
    Accepts query_list of organisations
    Accepts flag for kpi_name if only individual kpi_name requested
    """
    if kpi_name == "all":
        return (
            filtered_organisations.annotate(
                paediatrician_with_expertise_in_epilepsies_sum=Sum(
                    "kpi__paediatrician_with_expertise_in_epilepsies"
                )
            )
            .annotate(
                epilepsy_specialist_nurse_sum=Sum("kpi__epilepsy_specialist_nurse")
            )
            .annotate(tertiary_input_sum=Sum("kpi__tertiary_input"))
            .annotate(
                epilepsy_surgery_referral_sum=Sum("kpi__epilepsy_surgery_referral")
            )
            .annotate(ecg_sum=Sum("kpi__ecg"))
            .annotate(mri_sum=Sum("kpi__mri"))
            .annotate(
                assessment_of_mental_health_issues_sum=Sum(
                    "kpi__assessment_of_mental_health_issues"
                )
            )
            .annotate(mental_health_support_sum=Sum("kpi__mental_health_support"))
            .annotate(
                comprehensive_care_planning_agreement_sum=Sum(
                    "kpi__comprehensive_care_planning_agreement"
                )
            )
            .annotate(
                patient_held_individualised_epilepsy_document_sum=Sum(
                    "kpi__patient_held_individualised_epilepsy_document"
                )
            )
            .annotate(
                care_planning_has_been_updated_when_necessary_sum=Sum(
                    "kpi__care_planning_has_been_updated_when_necessary"
                )
            )
            .annotate(
                comprehensive_care_planning_content_sum=Sum(
                    "kpi__comprehensive_care_planning_content"
                )
            )
            .annotate(
                parental_prolonged_seizures_care_plan_sum=Sum(
                    "kpi__parental_prolonged_seizures_care_plan"
                )
            )
            .annotate(water_safety_sum=Sum("kpi__water_safety"))
            .annotate(first_aid_sum=Sum("kpi__first_aid"))
            .annotate(
                general_participation_and_risk_sum=Sum(
                    "kpi__general_participation_and_risk"
                )
            )
            .annotate(service_contact_details_sum=Sum("kpi__service_contact_details"))
            .annotate(sudep_sum=Sum("kpi__sudep"))
            .annotate(
                school_individual_healthcare_plan_sum=Sum(
                    "kpi__school_individual_healthcare_plan"
                )
            )
        )
    else:
        ans = filtered_organisations.annotate(kpi_sum=Sum(f"kpi__{kpi_name}"))
        return ans
