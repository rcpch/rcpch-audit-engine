"""Helper class for creating an answer set for E12CaseFactory constructor. See KPIMetric Class docstrings for details.

Details on what fields are being set inside factories according to KPI PASS | FAIL | INELIGIBLE:

- KPI 1
    - PASS:
        registration__assessment__pass_paediatrician_with_expertise_in_epilepsies=True
    - FAIL:
        registration__assessment__fail_paediatrician_with_expertise_in_epilepsies=True

- KPI 2
    - PASS:
        registration__assessment__pass_epilepsy_specialist_nurse=True
    - FAIL:
        registration__assessment__fail_epilepsy_specialist_nurse=True

- KPI 3 + 5 ELIGIBILITY FLAG
> NOTE: Due to eligibility reasons, KPI3+5 eligible only when age is 1y (<2y), KPI 6+8+10 only eligible when age is 12y(>=12y).
    eligible_kpi_3_5_ineligible_6_8_10=True,

- KPI 3 & 3b > NOTE: IF either PASS/FAIL flags set here, eligible_kpi_3_5_ineligible_6_8_10 must be used!
    - PASS:
        registration__assessment__pass_tertiary_input_AND_epilepsy_surgery_referral=True,
    - FAIL:
        registration__assessment__fail_tertiary_input_AND_epilepsy_surgery_referral=True,

- KPI 4
    - PASS:
        registration__epilepsy_context__pass_ecg=True,
        registration__investigations__pass_ecg=True,
    - FAIL:
        registration__epilepsy_context__fail_ecg=True,
        registration__investigations__fail_ecg=True,
    - INELIGIBLE:
        registration__epilepsy_context__ineligible_ecg=True,

- KPI 5 > NOTE: IF either PASS/FAIL flags set here, eligible_kpi_3_5_ineligible_6_8_10 must be used!
    - PASS:
        registration__investigations__pass_mri=True,
    - FAIL:
        registration__investigations__fail_mri=True,

- KPI 6
    > NOTE: If either PASS/FAIL flags set here, must use flag eligible_kpi_6_8_10_ineligible_3_5.
    - PASS:
        pass_assessment_of_mental_health_issues=True,
        registration__pass_assessment_of_mental_health_issues=True,
        registration__multiaxial_diagnosis__pass_assessment_of_mental_health_issues=True,
    - FAIL:
        fail_assessment_of_mental_health_issues=True,
        registration__fail_assessment_of_mental_health_issues=True,
        registration__multiaxial_diagnosis__fail_assessment_of_mental_health_issues=True,

- KPI 7
    - PASS:
        registration__multiaxial_diagnosis__pass_mental_health_support=True,
        registration__management__pass_mental_health_support=True,
    - FAIL:
        registration__multiaxial_diagnosis__fail_mental_health_support=True,
        registration__management__fail_mental_health_support=True,
    - INELIGIBLE:
        registration__multiaxial_diagnosis__ineligible_mental_health_support=True,

- KPI 8 
    > NOTE: If either PASS/FAIL flags set here, must use flag eligible_kpi_6_8_10_ineligible_3_5.
    - PASS:
        pass_sodium_valproate = True,
        registration__management__sodium_valproate = 'pass',
    - FAIL:
        fail_sodium_valproate = True,
        registration__management__sodium_valproate = 'fail',
        
- KPI 9
> NOTE: as these sub-measures are all related, and flags are applied sequentially, we can only set ALL to pass or ALL to fail.
    - PASS
        registration__management__pass_kpi_9=True,
    - FAIL
    > NOTE: if fail flag set, parental_prolonged_seizures_care_plan is set to ineligible (due to is_rescue_medicine_prescribed=False)
        registration__management__fail_kpi_9=True,

- KPI 10
> NOTE: NOTE: If either PASS/FAIL flags set here, must use flag eligible_kpi_6_8_10_ineligible_3_5.
    - PASS
        pass_school_individual_healthcare_plan = True,
        registration__management__pass_school_individual_healthcare_plan=True,
    - FAIL
        fail_school_individual_healthcare_plan = True,
        registration__management__fail_school_individual_healthcare_plan=True,
"""
from typing import Literal

from epilepsy12.constants import SEX_TYPE


class KPIMetric:
    """
    Helper Class to feed in valid KPI PASS/FAIL/INELIGIBLE metrics to the e12_case_factory.

    Returns a dictionary of keyword arguments which can be passed into the E12CaseFactory constructor to produce a completed audit according to provided values.
    
    Usage:
    
        1. Instantiate a KPIMetric object, providing True/False values for BOTH `eligible_kpi_3_5` and `eligible_kpi_6_8_10`. One must be True, the other False.
        
            NOTE: this is because different age ranges determine eligibility of these 5 KPIs. To simplify the process of generating fake Cases, it was decided to condense the possibility space to just age=1yo (eligible for KPI 3 & 5), and age=12yo (eligible for KPI 6,8,10).
        
        2. Use the .generate_metrics() method to return dictionary of keyword args. You must provide a value for each of the following KPIs, depending on whether `eligible_kpi_3_5` + `eligible_kpi_6_8_10` were True/False.

            NOTE: a KeyError is raised if the required KPI kwarg is not provided.
        
            `eligible_kpi_3_5=True`, kwargs and values to provide:
            
                - kpi_1 = 'PASS' OR 'FAIL'
                - kpi_2 = 'PASS' OR 'FAIL'
                - kpi_3 = 'PASS' OR 'FAIL' -> NOTE: eligibility is set in constructor.
                - kpi_4 = 'PASS' OR 'FAIL' OR 'INELIGIBLE'
                - kpi_5 = 'PASS' OR 'FAIL' -> NOTE: eligibility is set in constructor.
                - kpi_7 = 'PASS' OR 'FAIL' OR 'INELIGIBLE'
                - kpi_9 = 'PASS' OR 'FAIL'
            
            `eligible_kpi_6_8_10=True`, kwargs and values to provide:
            
                - kpi_1 = 'PASS' OR 'FAIL'
                - kpi_2 = 'PASS' OR 'FAIL'
                - kpi_4 = 'PASS' OR 'FAIL' OR 'INELIGIBLE'
                - kpi_6 = 'PASS' OR 'FAIL' -> NOTE: eligibility is set in constructor.
                - kpi_7 = 'PASS' OR 'FAIL' OR 'INELIGIBLE'
                - kpi_8 = 'PASS' OR 'FAIL' -> NOTE: eligibility is set in constructor.
                - kpi_9 = 'PASS' OR 'FAIL'
                - kpi_10 = 'PASS' OR 'FAIL' -> NOTE: eligibility is set in constructor.
    
    Example usage:

    ```python
    
    metric_3_5_eligible = KPIMetric(eligible_kpi_3_5=True, eligible_kpi_6_8_10=False)
    metric_kpi_6_8_10_eligible = KPIMetric(eligible_kpi_3_5=False, eligible_kpi_6_8_10=True)
    
    answer_set_1 = metric_3_5_eligible.generate_metrics(
        kpi_1='PASS',
        kpi_2='PASS',
        kpi_3='PASS',
        kpi_4='INELIGIBLE',
        kpi_5='FAIL',
        kpi_7='PASS',
        kpi_9='PASS',
    )
    answer_set_2 = metric_kpi_6_8_10_eligible.generate_metrics(
        kpi_1='PASS',
        kpi_2='PASS',
        kpi_4='INELIGIBLE',
        kpi_6='FAIL',
        kpi_7='PASS',
        kpi_8='PASS',
        kpi_9='FAIL',
        kpi_10='PASS',
    )
    
    case_1 = e12_case_factory(**answer_set_1)
    case_2 = e12_case_factory(**answer_set_2)
    """

    def __init__(self, eligible_kpi_3_5: bool=False, eligible_kpi_6_8_10: bool=False):
        if eligible_kpi_3_5 and eligible_kpi_6_8_10:
            raise ValueError(
                "Only one of the eligibility variables can be True. Currently both are set True."
            )

        self.eligible_kpi_3_5 = eligible_kpi_3_5
        self.eligible_kpi_6_8_10 = eligible_kpi_6_8_10

    # Each of these Class properties define the FactoryBoy flags which need to be set inside the e12CaseFactory constructor for that KPI to be a PASS | FAIL | INVALID.
    
    @property
    def PASS_KPI_1(self):
        return {
            "registration__assessment__pass_paediatrician_with_expertise_in_epilepsies": True,
        }

    @property
    def FAIL_KPI_1(self):
        return {
            "registration__assessment__fail_paediatrician_with_expertise_in_epilepsies": True
        }

    @property
    def PASS_KPI_2(self):
        return {
            "registration__assessment__pass_epilepsy_specialist_nurse": True,
        }

    @property
    def FAIL_KPI_2(self):
        return {
            "registration__assessment__fail_epilepsy_specialist_nurse": True,
        }

    @property
    def PASS_KPI_3(self):
        return {
            "registration__assessment__pass_tertiary_input_AND_epilepsy_surgery_referral": True,
        }

    @property
    def FAIL_KPI_3(self):
        return {
            "registration__assessment__fail_tertiary_input_AND_epilepsy_surgery_referral": True,
        }

    @property
    def PASS_KPI_4(self):
        return {
            "registration__epilepsy_context__pass_ecg": True,
            "registration__investigations__pass_ecg": True,
        }

    @property
    def FAIL_KPI_4(self):
        return {
            "registration__epilepsy_context__fail_ecg": True,
            "registration__investigations__fail_ecg": True,
        }

    @property
    def INELIGIBLE_KPI_4(self):
        return {
            "registration__epilepsy_context__ineligible_ecg": True,
        }

    @property
    def PASS_KPI_5(self):
        return {
            "registration__investigations__pass_mri": True,
        }

    @property
    def FAIL_KPI_5(self):
        return {
            "registration__investigations__fail_mri": True,
        }

    @property
    def PASS_KPI_6(self):
        return {
            "pass_assessment_of_mental_health_issues": True,
            "registration__pass_assessment_of_mental_health_issues": True,
            "registration__multiaxial_diagnosis__pass_assessment_of_mental_health_issues": True,
        }

    @property
    def FAIL_KPI_6(self):
        return {
            "fail_assessment_of_mental_health_issues": True,
            "registration__fail_assessment_of_mental_health_issues": True,
            "registration__multiaxial_diagnosis__fail_assessment_of_mental_health_issues": True,
        }

    @property
    def PASS_KPI_7(self):
        return {
            "registration__multiaxial_diagnosis__pass_mental_health_support": True,
            "registration__management__pass_mental_health_support": True,
        }

    @property
    def FAIL_KPI_7(self):
        return {
            "registration__multiaxial_diagnosis__fail_mental_health_support": True,
            "registration__management__fail_mental_health_support": True,
        }

    @property
    def INELIGIBLE_KPI_7(self):
        return {
            "registration__multiaxial_diagnosis__ineligible_mental_health_support": True,
        }

    @property
    def PASS_KPI_8(self):
        return {
            "pass_sodium_valproate": True,
            "registration__management__sodium_valproate": "pass",
        }

    @property
    def FAIL_KPI_8(self):
        return {
            "fail_sodium_valproate": True,
            "registration__management__sodium_valproate": "fail",
        }

    @property
    def PASS_KPI_9(self):
        return {
            "registration__management__pass_kpi_9": True,
        }

    @property
    def FAIL_KPI_9(self):
        return {
            "registration__management__fail_kpi_9": True,
        }

    @property
    def PASS_KPI_10(self):
        return {
            "pass_school_individual_healthcare_plan": True,
            "registration__management__pass_school_individual_healthcare_plan": True,
        }

    @property
    def FAIL_KPI_10(self):
        return {
            "fail_school_individual_healthcare_plan": True,
            "registration__management__fail_school_individual_healthcare_plan": True,
        }

    def check_value_allowed(self, kpi: str, value: str, add_ineligible: bool = False):
        """Raise value error if provided value not in list of available values."""
        available_values = ["PASS", "FAIL"]
        if add_ineligible:
            available_values += ["INELIGIBLE"]
        if value not in available_values:
            raise ValueError(
                f"Incorrect value provided for {kpi}: {value}. Available values are {available_values}"
            )

    def generate_metrics(self, **kwargs: Literal["PASS", "FAIL"])->dict:
        """
        Generate a dictionary of flags according to KPI metrics.
        """
        
        e12_case_factory_constructor_args = {}

        # Determine which age-dependent eligible KPI values can be used:
        if self.eligible_kpi_3_5:
            # add relevant fields age fields to return dict to set eligibility
            e12_case_factory_constructor_args.update(
                {"eligible_kpi_3_5_ineligible_6_8_10": True}
            )

            # NOT eligible for kpi 6,8,10
            for kpi in kwargs.keys():
                if kpi in ["kpi_6", "kpi_8", "kpi_10"]:
                    raise ValueError(
                        f"{self.eligible_kpi_3_5=} and {self.eligible_kpi_6_8_10=}. {kpi} can not be used as automatically set ineligible."
                    )

            # KPI 3 FIELDS TO ADD
            self.check_value_allowed(kpi="kpi_3", value=kwargs["kpi_3"])
            if kwargs["kpi_3"] == "PASS":
                e12_case_factory_constructor_args.update(self.PASS_KPI_3)
            else:
                e12_case_factory_constructor_args.update(self.FAIL_KPI_3)

            # KPI 5 FIELDS TO ADD
            self.check_value_allowed(kpi="kpi_5", value=kwargs["kpi_5"])
            if kwargs["kpi_5"] == "PASS":
                e12_case_factory_constructor_args.update(self.PASS_KPI_5)
            elif kwargs["kpi_5"] == "FAIL":
                e12_case_factory_constructor_args.update(self.FAIL_KPI_5)

        # eligible_kpi_6_8_10=True
        else:
            # add relevant fields to return dict to set eligibility
            e12_case_factory_constructor_args.update(
                {
                    "eligible_kpi_6_8_10_ineligible_3_5": True,
                    "sex" : SEX_TYPE[2][0],
                    # extra ineligibility kpi 3
                    "registration__assessment__ineligible_tertiary_input_AND_epilepsy_surgery_referral": True,
                    # extra ineligibility kpi5
                    "registration__ineligible_mri": True,
                    "registration__multiaxial_diagnosis__ineligible_mri": True,
                    "registration__multiaxial_diagnosis__syndrome_entity__ineligible_mri": True,
                }
            )

            # NOT eligible for 3,5
            for kpi in kwargs.keys():
                if kpi in ["kpi_3", "kpi_5"]:
                    raise ValueError(
                        f"{self.eligible_kpi_3_5=} and {self.eligible_kpi_6_8_10=}. {kpi} can not be used as automatically set ineligible."
                    )

            # KPI 6 FIELDS TO ADD
            self.check_value_allowed(kpi="kpi_6", value=kwargs["kpi_6"])
            if kwargs["kpi_6"] == "PASS":
                e12_case_factory_constructor_args.update(self.PASS_KPI_6)
            elif kwargs["kpi_6"] == "FAIL":
                e12_case_factory_constructor_args.update(self.FAIL_KPI_6)

            # KPI 8 FIELDS TO ADD
            self.check_value_allowed(kpi="kpi_8", value=kwargs["kpi_8"])
            if kwargs["kpi_8"] == "PASS":
                e12_case_factory_constructor_args.update(self.PASS_KPI_8)
            elif kwargs["kpi_8"] == "FAIL":
                e12_case_factory_constructor_args.update(self.FAIL_KPI_8)

            # KPI 10 FIELDS TO ADD
            self.check_value_allowed(kpi="kpi_10", value=kwargs["kpi_10"])
            if kwargs["kpi_10"] == "PASS":
                e12_case_factory_constructor_args.update(self.PASS_KPI_10)
            elif kwargs["kpi_10"] == "FAIL":
                e12_case_factory_constructor_args.update(self.FAIL_KPI_10)

        # Go through and add non age-dependent fields

        # KPI 1 FIELDS TO ADD
        self.check_value_allowed(kpi="kpi_1", value=kwargs["kpi_1"])
        if kwargs["kpi_1"] == "PASS":
            e12_case_factory_constructor_args.update(self.PASS_KPI_1)
        else:
            e12_case_factory_constructor_args.update(self.FAIL_KPI_1)

        # KPI 2 FIELDS TO ADD
        self.check_value_allowed(kpi="kpi_2", value=kwargs["kpi_2"])
        if kwargs["kpi_2"] == "PASS":
            e12_case_factory_constructor_args.update(self.PASS_KPI_2)
        else:
            e12_case_factory_constructor_args.update(self.FAIL_KPI_2)

        # KPI 4 FIELDS TO ADD
        self.check_value_allowed(
            kpi="kpi_4", value=kwargs["kpi_4"], add_ineligible=True
        )
        if kwargs["kpi_4"] == "PASS":
            e12_case_factory_constructor_args.update(self.PASS_KPI_4)
        elif kwargs["kpi_4"] == "FAIL":
            e12_case_factory_constructor_args.update(self.FAIL_KPI_4)
        else:
            e12_case_factory_constructor_args.update(self.INELIGIBLE_KPI_4)

        # KPI 7 FIELDS TO ADD
        self.check_value_allowed(
            kpi="kpi_7", value=kwargs["kpi_7"], add_ineligible=True
        )
        if kwargs["kpi_7"] == "PASS":
            e12_case_factory_constructor_args.update(self.PASS_KPI_7)
        elif kwargs["kpi_7"] == "FAIL":
            e12_case_factory_constructor_args.update(self.FAIL_KPI_7)
        else:
            e12_case_factory_constructor_args.update(self.INELIGIBLE_KPI_7)

        # KPI 9 FIELDS TO ADD
        self.check_value_allowed(kpi="kpi_9", value=kwargs["kpi_9"])
        if kwargs["kpi_9"] == "PASS":
            e12_case_factory_constructor_args.update(self.PASS_KPI_9)
        else:
            e12_case_factory_constructor_args.update(self.FAIL_KPI_9)

        return e12_case_factory_constructor_args
