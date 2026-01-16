---
title: Key Performance Indicators
reviewers: Dr Simon Chapman
---

The Key Performance Indicators are listed [here]('../clinician-users/clinician-user-guide.md##Audit Dataset')

the ```KPI``` model stores these indicators as individual fields, together with the help and reference text that is signposted in the template.

| Number | Label | Definition |
| -------- | ------| ----------| 
| 1. |  Paediatrician with expertise in Epilepsy within 2 weeks | % of children and young people with epilepsy, with input by a 'consultant paediatrician with expertise in epilepsies' within 2 weeks of initial referral |
| 2. |  Access to Epilepsy Specialist Nurse | % of children and young people with epilepsy, with input by epilepsy specialist nurse within the first year of care |
| 3a. | Tertiary Input | % of children and young people meeting defined criteria for paediatric neurology referral, with input of tertiary care and/or CESS referral within the first year of care |
| 3b. | Epilepsy Surgery Referral |% of ongoing children and young people meeting defined epilepsy surgery referral criteria with evidence of epilepsy surgery referral |
| 4. | ECG |% of children and young people with convulsive seizures and epilepsy, with an ECG at first year |
| 5. | MRI within 6 weeks | % of children and young people with defined indications for an MRI, who had timely MRI within 6 weeks of request |
| 6. | Assessment of Mental Health Issues | %  of children and young people with epilepsy where there is documented evidence that they have been asked about mental health either through clinical screening, or a questionnaire/measure |
| 7. | Mental Health Support | %  of children and young people with epilepsy and a mental health problem who have evidence of mental health support |
| 8. | Medication and Reproduction Risks | **in cohort 6:** % of all females 12 years and above currently on valproate treatment with annual risk acknowledgement form completed within first year of care<br>**in cohort 7 and above:** Percentage of females on valproate treatment and females aged 12 years and above on topiramate with a risk acknowledgement form completed or Pregnancy Prevention Programme in place within first year of care |
| 9a. | Care Planning Agreement | % of children and young people with epilepsy after 12 months where there is evidence of a comprehensive care plan that is agreed between the person, their family and/or carers and primary and secondary care providers, and the care plan has been updated where necessary |
| 9b. | Care Planning Components | % of children diagnosed with epilepsy with documented evidence of communication regarding core elements of care planning |
| 10. | School Individual Health Care Plan | % of children and young people with epilepsy aged 4 years and above with evidence of a school individual healthcare plan by 1 year after first paediatric assessment |

### 9a Care Planning Agreement | Definition

This item has 3 subheadings:

| Number | Label | Definition |
|----|----|------|
| 9a | Patient held individualised epilepsy document/copy of clinic letter that includes care planning information | % of children and young people with epilepsy after 12 months that had an individualised epilepsy document with individualised epilepsy document or a copy clinic letter that includes care planning information |
| 9b | Patient/carer/parent agreement to the care planning | % of children and young people with epilepsy after 12 months where there was evidence of agreement between the person, their family and/or carers as appropriate |
| 9c | Care planning has been updated when necessary | % of children and young people with epilepsy after 12 months where there is evidence that the care plan has been updated where necessary |

### 9b School Individual Health Care Plan

This has 6 subheadings

| Number | Label | Definition |
|----|----|------|
| 9a | Parental prolonged seizures care plan | Percentage of children and young people with epilepsy who have been prescribed rescue medication and have evidence of a written prolonged seizures plan. |
| 9b | Water safety | Percentage of children and young people with epilepsy with evidence of discussion regarding water safety. |
| 9c | First aid | Percentage of children and young people with epilepsy with evidence of discussion regarding first aid. |
| 9d | General participation and risk | Percentage of children and young people with epilepsy with evidence of discussion regarding general participation and risk. |
| 9e | SUDEP | Percentage of children and young people with epilepsy with evidence of discussion regarding SUDEP. |
| 9f | Service contact details | Percentage of children and young people with epilepsy with evidence of being given service contact details. |

Each query for each KPI is stored in a separate file within the `/common_view_functions/calculate_kpi_functions/` folder. The comment text at the head of each function documents the parameters of each query, the numerator and denominator.

## Scoring

Key performance indicators have 4 states:

- Failed (0)
- Passed (1)
- Ineligible (2)
- Unscored (None)

An example of an ineligible KPI would be a child with nonconvulsive epilepsy not needing an ECG.

This scoring system allows a child's individual score to be displayed clearly in the template using colours or icons to reflect their adherence to different measures, or for the scores to be aggregated together, for example to show how a give organisation performs against its peers in the same or another region. The results can be tabulated or mapped to show geographical variation, and sequentially against cohort to change over time.

The KPIs are final endpoint of the audit and therefore their accuracy is essential. A full suite of [tests](./testing/testing.md) is in place to ensure this is true.

Note that the KPIs are only calculated for the **currently submitting** cohort *that have completed a full year of care*

The KPIs are aggregated to generate totals and percentages as well as averages across different levels of abstraction - by this is meant, either at organisational level, trust/health board level, or NHS region etc.

They are key part of the [reporting](reporting.md) dashboard.
