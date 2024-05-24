---
title: Validating dates
reviewers: Dr Simon Chapman
---

## Overview

Dates are sparsely gathered across E12 as these are generally annoying for users to enter as they are slower to enter than other fields and involve digging back through clinical notes to find. Where they are collected, it is because something is calculated from them.

### First paediatric assessment date

Orginally this was registration_date, but was subsequently refactored to become first_paediatric_assessment_date. This is set in the registration form and is a one way value. Once set, it cannot be undone, except by RCPCH staff. It is a critical date, since cohort allocation and end of first year of care are both calculated from it. It is also used in date validation as the earliest allowable date for some measures.

### episode date

In the multiaxial diagnosis form, a child may have several episodes of seizure, each one associated with a date. Information is collected on confidence around that date, since many seizures are unwitnessed. The earliest allowable date an episode can be given is the date of birth.

### syndrome diagnosis date

In the multiaxial diagnosis form, a child may have more than one syndrome (though usually only one), each one associated with a date. The earliest allowable date a syndrome can be given is the date of birth.

### comordibidity diagnosis date

In the multiaxial diagnosis form, a child may have more than one comorbidity, each one associated with a date. The earliest allowable date a comorbidity can be given is the date of birth.

### Consultant paediatrician with expertise in epilepsies

2 dates are supplied and both are mandatory to complete the form - date referred and date seen
The date seen cannot be before the date referred and the earliest allowable date is the date of birth.

### Consultant paediatric neurologist

2 dates are supplied and both are mandatory to complete the form - date referred and date seen
The date seen cannot be before the date referred and the earliest allowable date is the first paediatric assessment date.

### Epilepsy surgery

Two dates are supplied if the child has been referred, but only the referral date is mandatory. The date seen cannot be before the date referred and the earliest allowable date is the first paediatric assessment date.

### Epilepsy nurse specialist

2 dates are supplied and both are mandatory to complete the form - date referred and date seen
The date seen cannot be before the date referred and the earliest allowable date is the first paediatric assessment date.

### EEG

2 dates are supplied and both are mandatory to complete the form - date requested and date performed
The date performed cannot be before the date requested and the earliest allowable date is the date of birth.

### MRI

2 dates are supplied and both are mandatory to complete the form - date requested and date performed
The date performed cannot be before the date requested and the earliest allowable date is the date of birth.

### Antiepilepsy medicine

#### antiseizure medicine

2 dates are supplied - date discontinued and date started -  but only date started is mandatory to complete the form if an antiseizure medicine has been given.

The date discontinued cannot be before the date started and the earliest allowable date is the date of first paediatric assessment.

#### rescue medicine

2 dates are supplied - date discontinued and date started -  but only date started is mandatory to complete the form if an antiseizure medicine has been given.

The date discontinued cannot be before the date started and the earliest allowable date is the date of first paediatric assessment.

### Individualised care plan date

One date is supplied. Earliest allowable date is the date of first paediatric assessment.

### Validation

Date validation occurs in `validators.py` and accepts a minimum of one date. If more than one date, a flag must be supplied to explain whether it is expected to be the earlier of the the two dates. The `earliest_allowable_date` parameter is an optional.

It raises a ValueError which is caught in the UI.

### Validation dates summary table

| Model | Date | mandatory | earliest allowable date | other flags |
| ---- | ---- | ---- | ---- | ---- |
| Registration | first_paediatric_assessment_date | Yes | current submitting cohort start date for clinicians or date_of_birth if RCPCH audit team |   |
| Episode | seizure_onset_date | Yes | date_of_birth |   |
| Syndrome | syndrome_diagnosis_date | Yes | date_of_birth |   |
| Comorbidity | comorbidity_diagnosis_date | Yes | date_of_birth |   |
| Assessment | consultant_paediatrician_referral_date | Yes | date_of_birth |   |
| Assessment | consultant_paediatrician_input_date | Yes | consultant_paediatrician_referral_date |   |
| Assessment | paediatric_neurologist_referral_date | Yes | first_paediatric_assessment_date |   |
| Assessment | paediatric_neurologist_input_date | Yes | paediatric_neurologist_referral_date |   |
| Assessment | childrens_epilepsy_surgical_service_referral_date | Yes | first_paediatric_assessment_date |   |
| Assessment | childrens_epilepsy_surgical_service_input_date | No | childrens_epilepsy_surgical_service_referral_date |   |
| Assessment | epilepsy_specialist_nurse_referral_date | Yes | first_paediatric_assessment_date |   |
| Assessment | epilepsy_specialist_nurse_input_date | Yes | epilepsy_specialist_nurse_referral_date |   |
| Investigations | eeg_request_date | Yes | date_of_birth |   |
| Investigations | eeg_performed_date | Yes | eeg_request_date |   |
| Investigations | mri_brain_requested_date | Yes | date_of_birth |   |
| Investigations | mri_brain_reported_date | Yes | mri_brain_requested_date |   |
| AntiepilepsyMedicine | antiepilepsy_medicine_start_date | Yes | first_paediatric_assessment_date | is_rescue = False   |
| AntiepilepsyMedicine | antiepilepsy_medicine_stop_date | No | antiepilepsy_medicine_start_date |  is_rescue = False |
| AntiepilepsyMedicine | antiepilepsy_medicine_start_date | Yes | first_paediatric_assessment_date | is_rescue = True   |
| AntiepilepsyMedicine | antiepilepsy_medicine_stop_date | No | antiepilepsy_medicine_start_date |  is_rescue = True |
| Management | individualised_care_plan_date | Yes | first_paediatric_assessment_date |   |
