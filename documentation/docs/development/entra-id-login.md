---
title: Microsoft Entra ID sign in
---

Superusers and members of the **RCPCH Audit Team** role can sign in with their RCPCH Microsoft account ("Sign in with Microsoft" on the login page) instead of the email address, password and one-time code login.

A setting can make this **compulsory** for them. It is off by default and can be switched off again at any time.

## Who it applies to

A user is covered if they are a superuser (`is_superuser`) **or** have the role `RCPCH_AUDIT_TEAM`. Everyone else keeps the email, password and one-time code login and cannot use Sign in with Microsoft.

## Environment variables

| Variable | Purpose |
|---|---|
| `ENTRA_ID_TENANT_ID` | Directory (tenant) id of the RCPCH Entra ID tenant. Only accounts from this tenant are accepted. |
| `ENTRA_ID_CLIENT_ID` | Application (client) id of the app registration. |
| `ENTRA_ID_CLIENT_SECRET` | Client secret of the app registration. |
| `ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF` | `"True"` to make Sign in with Microsoft compulsory for superusers and the RCPCH Audit Team. Defaults to `"False"`. |

Sign in with Microsoft is offered whenever the first three are all set. If `ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF` is `"True"` but they are not all set, the app refuses to start rather than lock every superuser out.

## Setting up the app registration

1. In the Entra admin centre, create an app registration for **accounts in this organisational directory only** (single tenant).
2. Add a **Web** redirect URI of `https://<site domain>/account/entra-id/callback/` for each environment (for example the live and staging domains).
3. Create a client secret and store it with the other secrets for the environment. Note its expiry date: when it expires, Sign in with Microsoft stops working (see [Switching it off](#switching-it-off)).
4. No API permissions are needed beyond the default `openid` / `profile` sign in.

Multi-factor authentication is enforced by RCPCH's own Entra ID (Conditional Access) policy, so a successful Sign in with Microsoft counts as the second factor. It is recorded against an "Entra ID" device on the user, which you can see on the user's logs page.

## How accounts are matched

The Microsoft account's email (`email`, `preferred_username` or `upn` claim) must match exactly one Epilepsy12 user's email address. On the first successful sign in, the Microsoft account's immutable object id is stored on the user's Entra ID device. Later sign ins must come from the same Microsoft account. If an RCPCH email address is ever reassigned to a different person, sign in is refused until the Entra ID device is deleted from the user's logs page (the same place two-factor devices are reset).

Failed sign ins are recorded in the user's visit activity as "Microsoft Entra ID login failed", with the reason.

## Switching it on

1. Set `ENTRA_ID_TENANT_ID`, `ENTRA_ID_CLIENT_ID` and `ENTRA_ID_CLIENT_SECRET` and deploy. Sign in with Microsoft now appears on the login page but is optional.
2. Ask every superuser and RCPCH Audit Team member to sign in with Microsoft once to check their account matches.
3. Set `ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF="True"` and deploy. From then on:
    - their email and password login is refused with a message telling them to sign in with Microsoft
    - any session they started with their password is ended on their next request

## Switching it off

Set `ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF="False"` (or remove it) and deploy. Nothing about anyone's account is changed when the setting is switched on: passwords, authenticator apps, email codes and backup codes are all kept. So once it is off, superusers and the RCPCH Audit Team can sign in with their email, password and one-time code again straight away.

Remove the three app registration variables as well to hide Sign in with Microsoft completely.
