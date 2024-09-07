# Scratchpad

This file is to write steps in a workflow. It is not a substitute for the docs.

## If a user fails to click on the confirm email link they cannot subsequently reset their password. Debug work flow

1. Set token expired to 2 minutes
2. create new user
3. check email_confirmed flag in admin as superuser
4. allow 2 minutes to expire
5. click on confirm email link as logged out user to confirm token has expired
6. Try and reset password as new user
