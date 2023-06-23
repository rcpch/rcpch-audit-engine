"""
## Delete Tests

    [] Assert an Audit Centre Administrator CANNOT delete users - HTTPStatus.FORBIDDEN
    [] Assert an audit centre clinician CANNOT delete users - HTTPStatus.FORBIDDEN
    [] Assert an Audit Centre Lead Clinician CANNOT delete users outside own Trust - HTTPStatus.FORBIDDEN

    [] Assert an Audit Centre Lead Clinician can delete users inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can delete users inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can delete users outside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can delete users inside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can delete users outside own Trust - HTTPStatus.OK
    
    
    
    [] Assert an Audit Centre Administrator CANNOT delete patients - HTTPStatus.FORBIDDEN
    [] Assert an audit centre clinician CANNOT delete patients outside own Trust - HTTPStatus.FORBIDDEN
    [] Assert an Audit Centre Lead Clinician CANNOT delete patients outside own Trust - HTTPStatus.FORBIDDEN

    [] Assert an Audit Centre Lead Clinician can delete patients inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can delete patients inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can delete patients outside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can delete patients inside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can delete patients outside own Trust - HTTPStatus.OK



    [] Assert an Audit Centre Administrator CANNOT delete patient_records - HTTPStatus.FORBIDDEN
    [] Assert an audit centre clinician CANNOT delete patient_records outside own Trust - HTTPStatus.FORBIDDEN
    [] Assert an Audit Centre Lead Clinician CANNOT delete patient_records outside own Trust - HTTPStatus.FORBIDDEN

    [] Assert an Audit Centre Lead Clinician can delete patient_records inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can delete patient_records inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can delete patient_records outside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can delete patient_records inside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can delete patient_records outside own Trust - HTTPStatus.OK

# Episode
[ ] Assert an Audit Centre Administrator cannot 'remove_episode' - response.status_code == 403
[ ] Assert an Audit Centre Clinician can 'remove_episode' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot 'remove_episode' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can 'remove_episode' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot 'remove_episode' inside a different Trust - response.status_code == 403
[ ] Assert RCPCH Audit Team can can 'remove_episode' inside any Trust - response.status_code == 200

# Syndrome
[ ] Assert an Audit Centre Administrator cannot 'remove_syndrome' - response.status_code == 403
[ ] Assert an Audit Centre Clinician can 'remove_syndrome' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot 'remove_syndrome' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can 'remove_syndrome' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot 'remove_syndrome' inside a different Trust - response.status_code == 403
[ ] Assert RCPCH Audit Team can can 'remove_syndrome' inside any Trust - response.status_code == 200

# Comorbidity
[ ] Assert an Audit Centre Administrator cannot 'remove_comorbidity' - response.status_code == 403
[ ] Assert an Audit Centre Clinician can 'remove_comorbidity' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot 'remove_comorbidity' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can 'remove_comorbidity' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot 'remove_comorbidity' inside a different Trust - response.status_code == 403
[ ] Assert RCPCH Audit Team can can 'remove_comorbidity' inside any Trust - response.status_code == 200

# Antiepilepsy Medicine
[ ] Assert an Audit Centre Administrator cannot 'remove_antiepilepsy_medicine' - response.status_code == 403
[ ] Assert an Audit Centre Clinician can 'remove_antiepilepsy_medicine' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot 'remove_antiepilepsy_medicine' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can 'remove_antiepilepsy_medicine' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot 'remove_antiepilepsy_medicine' inside a different Trust - response.status_code == 403
[ ] Assert RCPCH Audit Team can can 'remove_antiepilepsy_medicine' inside any Trust - response.status_code == 200
"""
