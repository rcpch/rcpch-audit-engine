---
title: Environment Variables
reviewers: Dr Marcus Baw
---

## Adding a new environment variable - checklist

When adding a new environment variable (ENV), please follow these steps:

1. Choose the ENV name carefully. It should be unambiguous, and should not be a common name that might be used by other software. It should be in uppercase, with underscores separating words. It should be descriptive, and should not be an abbreviation unless the abbreviation is widely understood.

1. Add the new ENV to the **non-committed** `envs/.env` file. This file should be used to set the environment variables for your local development. **This file should not be committed to the repository**. You can use real values for the environment variables in this file. **Group related ENVs together** in this file, following the style of the `env-template` file.

1. Add the new ENV to the `envs/env-template` file, which is the ONLY file in the /envs/ folder that should be committed to the repository. In this file you can set a **default/suggested value** for the variable (assuming that there is no security risk to disclosure of this), and add a **comment** to explain what it does. Commit and push this file to the repository. Group related ENVs together in this file, keeping it the same order as the `.env` file.

1. Usually the ENV's value will be accessed somewhere in `settings.py` with something like `os.getenv("ENV_VAR_NAME")`. Try to keep the ENV name consistent with the variable name used in the code. Also aim to **group related settings together** in the settings file.

1. Make the ENV available to GitHub Actions and the deployment environments. See below for details

### Pushing the ENVs to GitHub for Actions to use it

There is a script in the `s/` folder which uses the `gh` GitHub CLI tool to push the contents of your `envs/.env` file as a base64-encoded string to a *single* GitHub secret called ENVIRONMENT in the E12 repository. This is then used by the GitHub Actions to decode and supply the appropriate ENVs to the software stack during automated tests. You **can** safely push confidential information to this secret, as it is only accessible to the E12 repository.

### Pushing the ENVs to our deployment environments

At present the ENVs are manually copied into `/var/epilepsy12/envs/.env` in each of the deployment environments - Development, Staging and Live. This is done by the system administrator. It is possible that in future we will use a more automated system for this.

### Sharing the ENVs with other developers

All developers who have a local development environment are likely to need to be aware that there is a new ENV and what it does. One way to inform the team is using our secure Signal chat. Generally confidential ENV values are not shared by email or other insecure methods.

### Further documentation

Documentation about the environment variable is **only** required if it not immediately clear from the name and comments that it does and how it is used.
