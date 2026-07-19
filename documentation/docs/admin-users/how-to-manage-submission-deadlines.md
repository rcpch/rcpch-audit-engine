---
title: "How to manage submission deadlines"
author: Epilepsy12 team
---

Every cohort has an audit-wide submission deadline (the second Tuesday of January after the data collection year ends). Occasionally an organisation needs more time — for example because of staffing shortages or EPR problems — and the audit team can grant that organisation its own deadline extension from the organisation dashboard.

This can only be done by members of the **RCPCH audit team**.

## Granting an extension

1. Navigate to the organisation's dashboard (**Organisation** → select the organisation).
2. The three cohort cards at the top show the cohort dates. On the currently submitting (or grace) cohort card, click **Extend deadline**.
3. Enter the number of **days** to extend by and, optionally, a **reason**.
4. Click **Save extension**.

The card now shows the audit-wide deadline with a pink **Extended to …** badge underneath. The lead clinician(s) at the organisation and the audit team mailbox receive an email confirming the new deadline.

!!! note
    Extensions are given in **days added to the organisation's current deadline**. If an organisation already has an extension and you grant more time, the new days are added to the *extended* date, not the original audit-wide date — the button reads **Extend further** in this case.

## Closing submission early

If an organisation tells you it has finished entering data before its deadline, you can close its submission immediately:

1. On the cohort card, click **Close submission** (this button only appears when the organisation has an extension).
2. Confirm in the dialog.

Submission for that organisation closes at the end of today. The card shows a pink **Closed early: …** badge, and the lead clinician(s) and audit team are emailed.

## Removing an extension

If an extension was granted in error:

1. On the cohort card, click **Remove extension** (only visible when an extension exists).
2. Confirm in the dialog.

The organisation's deadline reverts to the audit-wide date and the lead clinician(s) and audit team are emailed.

!!! warning
    Extensions cannot be removed once the audit-wide deadline has passed — at that point the extension is part of the audit record of what the organisation submitted against.

## What organisations see

Organisation users see the same cohort cards (without the action buttons), including any **Extended to …** or **Closed early: …** badge and the countdown of days remaining, which always reflects their own effective deadline.

## Chasing late submissions

Once the audit-wide deadline has passed, any organisations still able to submit are doing so only because they hold an extension. To see them:

1. Open the **Django admin** and go to **Audit Period site extensions**.
2. Filter by cohort using the **Audit period** filter on the right.
3. Use the **Open past audit-wide deadline** filter and choose **Yes**.

The list shows each organisation still open past the audit-wide deadline, with the audit-wide date, their extended date, and the number of days remaining — the list of sites to chase before their extensions expire. Extensions whose own date has already passed drop off the list automatically.
