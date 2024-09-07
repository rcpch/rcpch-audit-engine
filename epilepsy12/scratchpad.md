# Scratchpad

This file is to write steps in a workflow. It is not a substitute for the docs.

## If a user fails to click on the confirm email link they cannot subsequently reset their password. Debug work flow

1. Set token expired to 2 minutes
2. create new user
3. check email_confirmed flag in admin as superuser
4. allow 2 minutes to expire
5. click on confirm email link as logged out user to confirm token has expired
   Option 1

- superuser clicks on resend email link and logs out
- user clicks on password reset email from this and resets password then logs in
- superuser checks admin

Option 2

- user has not confirmed account and that token has now expired
- user tries to reset password - they are in the gulag: no email is sent

1.  Try and reset password as new user


Items to fix



Observations
The newly created user with email_confirmed being false and token expired has is_active still true, password_last_set datetime is same as creation datetime
Option 1 workflow is working as expected: user has 

