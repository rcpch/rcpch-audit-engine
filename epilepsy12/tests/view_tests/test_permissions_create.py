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
"""