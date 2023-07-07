"""

## Create Tests

[] Assert an Audit Centre Administrator CANNOT create users
[] Assert an audit centre clinician CANNOT create users
[] Assert an Audit Centre Lead Clinician can only create users inside own Trust - response.status_code == 200
[] Assert an RCPCH Audit Lead can create users nationally, within any organisations  - response.status_code == 200

[] Assert an Audit Centre Administrator can only create patients within own organisation - response.status_code == 200
[] Assert an audit centre clinician  can only create patients within own organisation - response.status_code == 200
[] Assert an Audit Centre Lead Clinician can only create patients within own Trust - response.status_code == 200
[] Assert an RCPCH Audit Lead can create patients nationally, within any organisations - response.status_code == 200


[] Assert an Audit Centre Administrator CANNOT create patient records
[] Assert an audit centre clinician can only create patient records within own organisation - response.status_code == 200
[] Assert an Audit Centre Lead Clinician can only create patient records within own Trust - response.status_code == 200
[] Assert an RCPCH Audit Lead can create patient records nationally, within any organisations - response.status_code == 200

# Episode
[ ] Assert an Audit Centre Administrator cannot 'add_episode' - response.status_code == 403
[ ] Assert an Audit Centre Clinician can 'add_episode' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot 'add_episode' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can 'add_episode' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot 'add_episode' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can can 'add_episode' inside any Trust - response.status_code == 200

# Comorbidity
[ ] Assert an Audit Centre Administrator cannot 'add_comorbidity' - response.status_code == 403
[ ] Assert an Audit Centre Clinician can 'add_comorbidity' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot 'add_comorbidity' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can 'add_comorbidity' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot 'add_comorbidity' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can can 'add_comorbidity' inside any Trust - response.status_code == 200

# Syndrome
[ ] Assert an Audit Centre Administrator cannot 'add_syndrome' - response.status_code == 403
[ ] Assert an Audit Centre Clinician can 'add_syndrome' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot 'add_syndrome' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can 'add_syndrome' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot 'add_syndrome' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can can 'add_syndrome' inside any Trust - response.status_code == 200

# Antiepilepsy Medicine
[ ] Assert an Audit Centre Administrator cannot 'add_antiepilepsy_medicine' - response.status_code == 403
[ ] Assert an Audit Centre Clinician can 'add_antiepilepsy_medicine' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot 'add_antiepilepsy_medicine' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can 'add_antiepilepsy_medicine' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot 'add_antiepilepsy_medicine' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can can 'add_antiepilepsy_medicine' inside any Trust - response.status_code == 200
"""
