"""
9i. Percentage of children and young people with epilepsy after 12 months that had an individualised epilepsy document with individualised epilepsy document or a copy clinic letter that includes care planning information.

All must be true to pass
individualised_care_plan_in_place
individualised_care_plan_has_parent_carer_child_agreement
has_individualised_care_plan_been_updated_in_the_last_year

- [ ] Measure 9i passed (registration.kpi.comprehensive_care_planning_agreement == 1) if all true
- [ ] Measure 9i failed (registration.kpi.comprehensive_care_planning_agreement == 1) if individualised_care_plan_in_place == False and others not None
- [ ] Measure 9i failed (registration.kpi.comprehensive_care_planning_agreement == 1) if individualised_care_plan_has_parent_carer_child_agreement == False and others not None
- [ ] Measure 9i failed (registration.kpi.comprehensive_care_planning_agreement == 1) if has_individualised_care_plan_been_updated_in_the_last_year == False and others not None
"""
