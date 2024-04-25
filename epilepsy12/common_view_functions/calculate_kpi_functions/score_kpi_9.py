# python imports

# django imports

# E12 imports
from epilepsy12.constants import KPI_SCORE


def score_kpi_9A(registration_instance) -> int:
    """9A. comprehensive_care_planning_agreement

    % of children and young people with epilepsy after 12 months where there is evidence of a comprehensive care plan that is agreed between the person, their family and/or carers and primary and secondary care providers, and the care plan has been updated where necessary

    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy at first year AND ALL OF:
    1) an individualised epilepsy document or copy clinic letter that includes care planning information
    2) evidence of agreement
    3) care plan is up to date including elements where necessary

    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """

    management = registration_instance.management

    fields_not_filled = [
        (management.has_individualised_care_plan_been_updated_in_the_last_year is None),
        (management.individualised_care_plan_has_parent_carer_child_agreement is None),
    ]

    # unscored
    if management.individualised_care_plan_in_place is not None:
        if management.individualised_care_plan_in_place:
            if any(fields_not_filled):
                # there is a care plan in place but not yet known if updated in the last year or evidence of agreement not yet scored
                return KPI_SCORE["NOT_SCORED"]
        else:
            # there is no care plan in place
            return KPI_SCORE["FAIL"]
    else:
        return KPI_SCORE["NOT_SCORED"]

    # score kpi
    pass_criteria = [
        (management.individualised_care_plan_in_place is True),
        (management.has_individualised_care_plan_been_updated_in_the_last_year is True),
        (management.individualised_care_plan_has_parent_carer_child_agreement is True),
    ]

    if all(pass_criteria):
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_9Ai(registration_instance) -> int:
    """i. patient_held_individualised_epilepsy_document

    % of children and young people with epilepsy after 12 months that had an individualised epilepsy document with individualised epilepsy document or a copy clinic letter that includes care planning information

    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy at first year AND( with individualised epilepsy document or copy clinic letter that includes care planning information )

    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """

    # not scored

    management = registration_instance.management

    # unscored
    if management.individualised_care_plan_in_place is None:
        return KPI_SCORE["NOT_SCORED"]

    # score kpi
    if management.individualised_care_plan_in_place is True:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_9Aii(registration_instance) -> int:
    """ii patient_carer_parent_agreement_to_the_care_planning
    % of children and young people with epilepsy after 12 months where there was evidence of agreement between the person, their family and/or carers as appropriate

    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of agreement

    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """

    management = registration_instance.management

    # unscored measure if plan not in place is still a fail
    if management.individualised_care_plan_in_place is False:
        return KPI_SCORE["FAIL"]

    # unscored
    if management.individualised_care_plan_has_parent_carer_child_agreement is None:
        return KPI_SCORE["NOT_SCORED"]

    # score kpi
    elif management.individualised_care_plan_has_parent_carer_child_agreement is True:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_9Aiii(registration_instance) -> int:
    """iii. care_planning_has_been_updated_when_necessary

    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy at first year AND with care plan which is updated where necessary

    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """

    management = registration_instance.management

    # unscored measure if plan not in place is still a fail
    if management.individualised_care_plan_in_place is False:
        return KPI_SCORE["FAIL"]

    # unscored
    if management.has_individualised_care_plan_been_updated_in_the_last_year is None:
        return KPI_SCORE["NOT_SCORED"]

    # score kpi
    if management.has_individualised_care_plan_been_updated_in_the_last_year is True:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_9B(registration_instance) -> int:
    """9B. comprehensive_care_planning_content
    Percentage of children diagnosed with epilepsy with documented evidence of communication regarding core elements of care planning.

    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy at first year AND evidence of written prolonged seizures plan if prescribed rescue medication AND evidence of discussion regarding water safety AND first aid AND participation and risk AND service contact details AND SUDEP

    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """

    management = registration_instance.management

    fields_not_filled = [
        (management.has_rescue_medication_been_prescribed is None),
        (management.individualised_care_plan_parental_prolonged_seizure_care is None),
        (management.individualised_care_plan_include_first_aid is None),
        (management.individualised_care_plan_addresses_water_safety is None),
        (management.individualised_care_plan_includes_service_contact_details is None),
        (
            management.individualised_care_plan_includes_general_participation_risk
            is None
        ),
        (management.individualised_care_plan_addresses_sudep is None),
    ]

    # unscored
    if management.individualised_care_plan_in_place is not None:
        if management.individualised_care_plan_in_place:
            if any(fields_not_filled):
                # there is a care plan in place but not yet known if updated in the last year or evidence of agreement not yet scored
                return KPI_SCORE["NOT_SCORED"]
        else:
            # there is no care plan in place
            return KPI_SCORE["FAIL"]
    else:
        return KPI_SCORE["NOT_SCORED"]

    # unscored
    if any(fields_not_filled):
        return KPI_SCORE["NOT_SCORED"]

    # score kpi
    base_pass_criteria = [
        (management.individualised_care_plan_include_first_aid is True),
        (management.individualised_care_plan_addresses_water_safety is True),
        (management.individualised_care_plan_includes_service_contact_details is True),
        (
            management.individualised_care_plan_includes_general_participation_risk
            is True
        ),
        (management.individualised_care_plan_addresses_sudep is True),
    ]

    pass_1_criteria = [
        (management.has_rescue_medication_been_prescribed is False),
    ] + base_pass_criteria

    pass_2_criteria = [
        (management.has_rescue_medication_been_prescribed is True),
        (management.individualised_care_plan_parental_prolonged_seizure_care is True),
    ] + base_pass_criteria

    if all(pass_1_criteria) or all(pass_2_criteria):
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_9Bi(registration_instance) -> int:
    """9Bi. parental_prolonged_seizures_care_plan

    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy at first year AND prescribed rescue medication AND evidence of a written prolonged seizures plan

    Denominator = Number of children and young people diagnosed with epilepsy at first year AND prescribed rescue medication
    """

    management = registration_instance.management

    fields_not_filled = [
        (management.has_rescue_medication_been_prescribed is None),
        (management.individualised_care_plan_parental_prolonged_seizure_care is None),
    ]

    # unscored measure if plan not in place is still a fail
    if management.individualised_care_plan_in_place is False:
        return KPI_SCORE["FAIL"]

    # unscored
    if any(fields_not_filled):
        return KPI_SCORE["NOT_SCORED"]

    # ineligible
    if management.has_rescue_medication_been_prescribed is False:
        return KPI_SCORE["INELIGIBLE"]

    # score kpi
    if management.individualised_care_plan_parental_prolonged_seizure_care is True:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_9Bii(registration_instance) -> int:
    """ii. water_safety

    Percentage of children and young people with epilepsy with evidence of discussion regarding water safety.

    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding water safety

    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """

    management = registration_instance.management

    # unscored measure if plan not in place is still a fail
    if management.individualised_care_plan_in_place is False:
        return KPI_SCORE["FAIL"]

    # unscored
    if management.individualised_care_plan_addresses_water_safety is None:
        return KPI_SCORE["NOT_SCORED"]

    # score kpi
    if management.individualised_care_plan_addresses_water_safety is True:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_9Biii(registration_instance) -> int:
    """iii. first_aid

    Percentage of children and young people with epilepsy with evidence of discussion regarding first aid.

    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding first aid

    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """

    management = registration_instance.management

    # unscored measure if plan not in place is still a fail
    if management.individualised_care_plan_in_place is False:
        return KPI_SCORE["FAIL"]

    # unscored
    if management.individualised_care_plan_include_first_aid is None:
        return KPI_SCORE["NOT_SCORED"]

    # score kpi
    if management.individualised_care_plan_include_first_aid is True:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_9Biv(registration_instance) -> int:
    """iv. general_participation_and_risk

    Percentage of children and young people with epilepsy with evidence of discussion regarding general participation and risk.

    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding general participation and risk

    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """

    management = registration_instance.management

    # unscored measure if plan not in place is still a fail
    if management.individualised_care_plan_in_place is False:
        return KPI_SCORE["FAIL"]

    # unscored
    if management.individualised_care_plan_includes_general_participation_risk is None:
        return KPI_SCORE["NOT_SCORED"]

    # score kpi
    if management.individualised_care_plan_includes_general_participation_risk is True:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_9Bv(registration_instance) -> int:
    """v. service_contact_details

    Percentage of children and young people with epilepsy with evidence of discussion regarding SUDEP and evidence of a prolonged seizures care plan.

    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion of been given service contact details

    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """

    management = registration_instance.management

    # unscored measure if plan not in place is still a fail
    if management.individualised_care_plan_in_place is False:
        return KPI_SCORE["FAIL"]

    # unscored
    if management.individualised_care_plan_includes_service_contact_details is None:
        return KPI_SCORE["NOT_SCORED"]

    # score kpi
    if management.individualised_care_plan_includes_service_contact_details is True:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_9Bvi(registration_instance) -> int:
    """vi. sudep

    Percentage of children and young people with epilepsy with evidence of being given service contact details.

    Calculation Method

    Numerator = Number of children diagnosed with epilepsy AND had evidence of discussions regarding SUDEP

    Denominator = Number of children diagnosed with epilepsy at first year
    """

    management = registration_instance.management

    # unscored measure if plan not in place is still a fail
    if management.individualised_care_plan_in_place is False:
        return KPI_SCORE["FAIL"]

    fields_not_filled = [
        (management.individualised_care_plan_addresses_sudep is None),
    ]

    # unscored
    if any(fields_not_filled):
        return KPI_SCORE["NOT_SCORED"]

    # score kpi
    pass_criteria = [
        (management.individualised_care_plan_addresses_sudep is True),
    ]

    if all(pass_criteria):
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]
