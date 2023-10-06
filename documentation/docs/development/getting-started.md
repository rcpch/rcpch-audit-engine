---
title: Getting started
reviewers: Dr Marcus Baw
---

## Introduction

The RCPCH Audit Engine is a [Django](https://www.djangoproject.com/) 4.0 project, using [Semantic UI](https://semantic-ui.com/) for the user interface framework. It aims to standardise those elements of a national audit that can be standardised, such as the concept of a Case (patient), Registration of cases to the audit, and management of researchers and administration users. Each audit is likely to have some common features and some bespoke features, but the audit engine aims to make the common features easier to build.

## Python and Django

The RCPCH chose to use Python for developing the Digital Growth Charts and the Epilepsy12 platform, this was because it is an accessible yet trusted language, with an established reputation and userbase.

Django is a web framework for Python, which helps with developing a database-backed web application such as the E12 platform, providing structure, security features, and numerous prebuilt features and functionality which save time and reduce errors when developing.

In order to develop the platform you should have some familiarity with both of these technologies. Numerous online and free learning resources are available. [FreeCodeCamp](https://www.youtube.com/watch?v=eWRfhZUzrAc) has a full Python video course, and [CodeCademy](https://www.codecademy.com/learn/learn-python) offers an interactive online course. Many other similar courses are available, often for free online. Django itself has a great tutorial [here](https://docs.djangoproject.com/en/4.1/intro/tutorial01/).

## Git and GitHub

We use Git for local and remote version control, and GitHub to host our source code. We make use of the GitHub Issues feature for tracking our roadmap, features, and bugs. We use GitHub Pages for publishing some of our websites. We also use GitHub Projects to plan work.

We make use of Git branches extensively to manage parallel and concurrent workstreams. Development should always be done in a new branch and only merged with the live branch once suitable testing, review, and authorisation has occurred.

Deployment of our source code is automated where possible, mostly using GitHub Actions, in which a workflow file determines the deployment script, ensuring repeatable and dependable deployments.

## Open Source

The entire output of the RCPCH Incubator development team is open source. We believe in the importance of open source in the medical domain, which is a special humanitarian case in software terms.

Read more about this philosophy here - [Open Source is The Only Way For Medicine](https://blog.bawmedical.co.uk/open-source-is-the-only-way-for-medicine)

## Code Quality

Open source alone is not a guarantee of good safe code and so we adhere to the tech industry's best practices in terms of Python style guidance, linting, and testing.

## Security

Security is a very important aspect of managing projects such as these, and we use secure passwords, two-factor authentication, signed Git commits, branch protection, and keep all credentials in environment files. See [The Twelve-Factor App](https://12factor.net/) for the absolute textbook on this.

## Legal

Details of Information Governance, Clinical Safety and Medical Device registration can be viewed in the [Legal](../../legal/legal/) section.
