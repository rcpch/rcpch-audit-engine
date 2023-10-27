---
title: User workflow
reviewers: Dr Simon Chapman
---

Epilepsy12 has subclassed the BaseUserManager for Django. This maintains certain core Django features relating to password hashing and storage, but allows some customisation. The Epilepsy12 user therefore does not use 'username' as its primary identifier, rather it uses email.

## User creation

Signup is not user driven, and there is no capacity for account creation from the login page. Instead, lead clinicians are created by RCPCH audit team members through a user work flow accessible from the organisation landing page. It is possible, depending on permissions, from this point to create users for individual organisations, or RCPCH audit team members who have broader access but are not affiliated with any organisation. There are additionally a small number of clinicians who also are part of the RCPCH Epilepsy12 team and therefore have national access.

Depending on permission, users can view all users in a given Trust/Local Health Board, and allocate users accordingly. A user is created from a standard Django form (```epilepsy12/forms_folder/epilepsy12_user.py```), where role, name and email are entered. On submit, validation occurs in the standard Django way, and if the form ```is_valid```, this generates an email sent to the new user, who clicks on the individualised link (valid for 72 hours) to activate the account.

User management is controlled from the user table, by those with appropriate permissions. From the user table it is possible to:

1. add new users
2. edit user details or groups
3. delete users
4. see activity logs

### Password reset

This workflow is available from the login page and is the standard Django workflow, with css styling to personalise the forms (```templates/registration```) to match Epilepsy12 and RCPCH design guidelines.

### Resend password

If the user has not clicked on the link within 72 hours, or the email has been lost in junk, the administrator can send a further email from the newly created user form. The workflow is identical to user creation.
