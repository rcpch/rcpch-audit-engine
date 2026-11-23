---
title: Microsoft Entra ID sign in
---

Superusers and members of the **RCPCH Audit Team** role can sign in with their RCPCH Microsoft account ("Sign in with Microsoft" on the login page) instead of the email address, password and one-time code login.

A setting can make this **compulsory** for them. It is off by default and can be switched off again at any time.

## Who it applies to

A user is covered if they are a superuser (`is_superuser`) **or** have the role `RCPCH_AUDIT_TEAM`. Everyone else keeps the email, password and one-time code login and cannot use Sign in with Microsoft.

## The login page

The Sign in with Microsoft button is hidden until an email address on `ENTRA_ID_EMAIL_DOMAIN` (e.g. `@rcpch.ac.uk`) is typed into the email field. The password login stays available alongside it, so the audit team's lower-permission test accounts (e.g. `firstname.lastname+lead_clinician@rcpch.ac.uk`) still sign in with a password and one-time code.

Whether the button shows is decided from the typed address alone: in the browser, or by the server when the login page is shown again after a failed attempt, so it also works without JavaScript. It reveals nothing about whether an account exists or what kind it is.

The typed address is passed to Microsoft so the right account is pre-selected.

New RCPCH Audit Team members do not need a password: they leave the password field empty and click Sign in with Microsoft.

## Environment variables

| Variable | Purpose |
|---|---|
| `ENTRA_ID_TENANT_ID` | Directory (tenant) id of the RCPCH Entra ID tenant. Only accounts from this tenant are accepted. |
| `ENTRA_ID_CLIENT_ID` | Application (client) id of the app registration. |
| `ENTRA_ID_CLIENT_SECRET` | Client secret of the app registration. |
| `ENTRA_ID_EMAIL_DOMAIN` | e.g. `rcpch.ac.uk`. The button is shown for this domain, and only Microsoft accounts with an email on it are accepted. |
| `ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF` | `"True"` to make Sign in with Microsoft compulsory for superusers and the RCPCH Audit Team. Defaults to `"False"`. |
| `ENTRA_ID_REQUIRE_MFA_CLAIM` | Defaults to `"True"`: refuse a Microsoft sign in unless the ID token's `amr` claim includes `mfa`. See [Multi-factor authentication](#multi-factor-authentication). |

Sign in with Microsoft is enabled when the first four are all set. If `ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF` is `"True"` but they are not all set, the app refuses to start rather than lock every superuser out.

## Setting up the app registration

1. In the Entra admin centre, create an app registration for **accounts in this organisational directory only** (single tenant).
2. Add a **Web** redirect URI of `https://<site domain>/account/entra-id/callback/` for each environment (for example the live and staging domains).
3. Create a client secret and store it with the other secrets for the environment. Note its expiry date: when it expires, Sign in with Microsoft stops working (see [Switching it off](#switching-it-off)).
4. No API permissions are needed beyond the default `openid` / `profile` sign in.

## Multi-factor authentication

A successful Sign in with Microsoft counts as the second factor, so there is no Epilepsy12 one-time code. It is recorded against an "Entra ID" device on the user, which you can see on the user's logs page.

This relies on RCPCH's Entra ID Conditional Access policy requiring MFA for this app registration every time, including from any trusted or office networks. Confirm this with the tenant administrators before switching the setting on.

As a defence in depth, sign ins are refused unless the ID token's `amr` (authentication methods) claim includes `mfa`. **Check this on staging first:** if every sign in is refused with "did not use multi-factor authentication", the error email shows the `amr` value received. If the claim is missing from the tokens altogether, set `ENTRA_ID_REQUIRE_MFA_CLAIM="False"` and rely on the Conditional Access policy.

## How accounts are matched

The Microsoft account's email (`email`, `preferred_username` or `upn` claim) must be on `ENTRA_ID_EMAIL_DOMAIN` and match exactly one Epilepsy12 user's email address. Addresses on other domains are ignored, because a guest account in the tenant can carry an outside address.

On the first successful sign in, the Microsoft account's immutable object id is stored on the user's Entra ID device. Later sign ins must come from the same Microsoft account. If an RCPCH email address is ever reassigned to a different person, sign in is refused until the Entra ID device is deleted from the user's logs page (the same place two-factor devices are reset).

Failed sign ins are recorded in the user's visit activity as "Login failed", with details starting "Microsoft Entra ID sign in failed:" and the reason. They are also logged at error level, so the admins are emailed.

## Switching it on

1. Set the four Entra ID variables above and deploy. Sign in with Microsoft now appears for `@rcpch.ac.uk` addresses but is optional.
2. Ask every superuser and RCPCH Audit Team member to sign in with Microsoft once to check their account matches.
3. Set `ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF="True"` and deploy. From then on, their email and password login is refused with the same "incorrect email or password" error as a wrong password, so a correct password is never revealed. The real reason is recorded in their visit activity. Sessions already open when the setting is switched on carry on until they log out or are automatically logged out.

## Switching it off

Set `ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF="False"` (or remove it) and deploy. Nothing about anyone's account is changed when the setting is switched on: passwords, authenticator apps, email codes and backup codes are all kept. So once it is off, superusers and the RCPCH Audit Team can sign in with their email, password and one-time code again straight away.

Remove the Entra ID variables as well to hide Sign in with Microsoft completely.
