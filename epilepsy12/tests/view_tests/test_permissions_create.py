"""

## Create Tests

    [ ] Assert an Audit Centre Lead Clinician can create users inside own Trust - response.status_code == 200
    [ ] Assert RCPCH Audit Team can create users nationally, inside own Trust, and outside  - response.status_code == 200
    [ ] Assert Clinical Audit Team can create users nationally, inside own Trust, and outside  - response.status_code == 200

    [ ] Assert an Audit Centre Administrator CANNOT create users - response.status_code == 403
    [ ] Assert an audit centre clinician CANNOT create users - response.status_code == 403
    [ ] Assert an Audit Centre Lead Clinician CANNOT create users outside own Trust - response.status_code == 403


    [ ] Assert an Audit Centre Administrator can create patients inside own Trust - response.status_code == 200
    [ ] Assert an Audit Centre Clinician can create patients inside own Trust - response.status_code == 200
    [ ] Assert an Audit Centre Lead Clinician can create patients inside own Trust - response.status_code == 200
    [ ] Assert RCPCH Audit Team can create patients nationally, inside own Trust, and outside  - response.status_code == 200
    [ ] Assert Clinical Audit Team can create patients nationally, inside own Trust, and outside  - response.status_code == 200

    [ ] Assert an Audit Centre Administrator CANNOT create patients outside own Trust - response.status_code == 403
    [ ] Assert an audit centre clinician CANNOT create patients outside own Trust - response.status_code == 403
    [ ] Assert an Audit Centre Lead Clinician CANNOT create patients outside own Trust - response.status_code == 403


    [ ] Assert an Audit Centre Clinician can create patient records inside own Trust - response.status_code == 200
    [ ] Assert an Audit Centre Lead Clinician can create patient records inside own Trust - response.status_code == 200
    [ ] Assert RCPCH Audit Team can create patient records nationally, inside own Trust, and outside  - response.status_code == 200
    [ ] Assert Clinical Audit Team can create patient records nationally, inside own Trust, and outside  - response.status_code == 200

    [ ] Assert an Audit Centre Administrator CANNOT create patient records - response.status_code == 403
    [ ] Assert an audit centre clinician CANNOT create patient records outside own Trust - response.status_code == 403
    [ ] Assert an Audit Centre Lead Clinician CANNOT create patient records outside own Trust - response.status_code == 403



# Episode

    [ ] Assert an Audit Centre Clinician can 'add_episode' inside own Trust - response.status_code == 200
    [ ] Assert an Audit Centre Lead Clinician can 'add_episode' inside own Trust - response.status_code == 200
    [ ] Assert RCPCH Audit Team can 'add_episode' inside own Trust - response.status_code == 200
    [ ] Assert Clinical Audit Team can 'add_episode' inside own Trust - response.status_code == 200
    [ ] Assert RCPCH Audit Team can 'add_episode' inside different Trust - response.status_code == 200
    [ ] Assert Clinical Audit Team can 'add_episode' inside different Trust - response.status_code == 200
    
    [ ] Assert an Audit Centre Administrator CANNOT 'add_episode' - response.status_code == 403
    [ ] Assert an Audit Centre Clinician CANNOT 'add_episode' outside own Trust - response.status_code == 403
    [ ] Assert an Audit Centre Lead Clinician CANNOT 'add_episode' outside own Trust - response.status_code == 403

# Comorbidity

    [ ] Assert an Audit Centre Clinician can 'add_comorbidity' inside own Trust - response.status_code == 200
    [ ] Assert an Audit Centre Lead Clinician can 'add_comorbidity' inside own Trust - response.status_code == 200
    [ ] Assert RCPCH Audit Team can 'add_comorbidity' inside own Trust - response.status_code == 200
    [ ] Assert Clinical Audit Team can 'add_comorbidity' inside own Trust - response.status_code == 200
    [ ] Assert RCPCH Audit Team can 'add_comorbidity' inside different Trust - response.status_code == 200
    [ ] Assert Clinical Audit Team can 'add_comorbidity' inside different Trust - response.status_code == 200
    
    [ ] Assert an Audit Centre Administrator CANNOT 'add_comorbidity' - response.status_code == 403
    [ ] Assert an Audit Centre Clinician CANNOT 'add_comorbidity' outside own Trust - response.status_code == 403
    [ ] Assert an Audit Centre Lead Clinician CANNOT 'add_comorbidity' outside own Trust - response.status_code == 403

# Syndrome

    [ ] Assert an Audit Centre Clinician can 'add_syndrome' inside own Trust - response.status_code == 200
    [ ] Assert an Audit Centre Lead Clinician can 'add_syndrome' inside own Trust - response.status_code == 200
    [ ] Assert RCPCH Audit Team can 'add_syndrome' inside own Trust - response.status_code == 200
    [ ] Assert Clinical Audit Team can 'add_syndrome' inside own Trust - response.status_code == 200
    [ ] Assert RCPCH Audit Team can 'add_syndrome' inside different Trust - response.status_code == 200
    [ ] Assert Clinical Audit Team can 'add_syndrome' inside different Trust - response.status_code == 200
    
    [ ] Assert an Audit Centre Administrator CANNOT 'add_syndrome' - response.status_code == 403
    [ ] Assert an Audit Centre Clinician CANNOT 'add_syndrome' outside own Trust - response.status_code == 403
    [ ] Assert an Audit Centre Lead Clinician CANNOT 'add_syndrome' outside own Trust - response.status_code == 403


# Antiepilepsy Medicine

    [ ] Assert an Audit Centre Clinician can 'add_antiepilepsy_medicine' inside own Trust - response.status_code == 200
    [ ] Assert an Audit Centre Lead Clinician can 'add_antiepilepsy_medicine' inside own Trust - response.status_code == 200
    [ ] Assert RCPCH Audit Team can 'add_antiepilepsy_medicine' inside own Trust - response.status_code == 200
    [ ] Assert Clinical Audit Team can 'add_antiepilepsy_medicine' inside own Trust - response.status_code == 200
    [ ] Assert RCPCH Audit Team can 'add_antiepilepsy_medicine' inside different Trust - response.status_code == 200
    [ ] Assert Clinical Audit Team can 'add_antiepilepsy_medicine' inside different Trust - response.status_code == 200
    
    [ ] Assert an Audit Centre Administrator CANNOT 'add_antiepilepsy_medicine' - response.status_code == 403
    [ ] Assert an Audit Centre Clinician CANNOT 'add_antiepilepsy_medicine' outside own Trust - response.status_code == 403
    [ ] Assert an Audit Centre Lead Clinician CANNOT 'add_antiepilepsy_medicine' outside own Trust - response.status_code == 403
"""
