"""
## Delete Tests

[] Assert an Audit Centre Administrator CANNOT delete users
[] Assert an audit centre clinician CANNOT delete users
[] Assert an Audit Centre Lead Clinician can only delete users inside own Trust
[] Assert an RCPCH Audit Lead can delete users nationally, within any organisations 

[] Assert an Audit Centre Administrator can only delete patients within own organisation
[] Assert an audit centre clinician  can only delete patients within own organisation
[] Assert an Audit Centre Lead Clinician can only delete patients within own Trust
[] Assert an RCPCH Audit Lead can delete patients nationally, within any organisations

[] Assert an Audit Centre Administrator CANNOT delete patient records
[] Assert an audit centre clinician can only delete patient records within own organisation
[] Assert an Audit Centre Lead Clinician can only delete patient records within own Trust
[] Assert an RCPCH Audit Lead can delete patient records nationally, within any organisations

# Episode
[ ] Assert an Audit Centre Administrator cannot 'remove_episode' - response.status_code == 403
[ ] Assert an Audit Centre Clinician can 'remove_episode' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot 'remove_episode' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can 'remove_episode' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot 'remove_episode' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can can 'remove_episode' inside any Trust - response.status_code == 200

# Syndrome
[ ] Assert an Audit Centre Administrator cannot 'remove_syndrome' - response.status_code == 403
[ ] Assert an Audit Centre Clinician can 'remove_syndrome' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot 'remove_syndrome' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can 'remove_syndrome' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot 'remove_syndrome' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can can 'remove_syndrome' inside any Trust - response.status_code == 200

# Comorbidity
[ ] Assert an Audit Centre Administrator cannot 'remove_comorbidity' - response.status_code == 403
[ ] Assert an Audit Centre Clinician can 'remove_comorbidity' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot 'remove_comorbidity' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can 'remove_comorbidity' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot 'remove_comorbidity' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can can 'remove_comorbidity' inside any Trust - response.status_code == 200

# Antiepilepsy Medicine
[ ] Assert an Audit Centre Administrator cannot 'remove_antiepilepsy_medicine' - response.status_code == 403
[ ] Assert an Audit Centre Clinician can 'remove_antiepilepsy_medicine' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot 'remove_antiepilepsy_medicine' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can 'remove_antiepilepsy_medicine' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot 'remove_antiepilepsy_medicine' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can can 'remove_antiepilepsy_medicine' inside any Trust - response.status_code == 200
"""
