---
title: Environment Variables
reviewers: Dr Marcus Baw
---

## Adding a new environment variable - checklist

When adding a new environment variable (env var), please follow these steps:

* Choose the env var name carefully. It should be unambiguous, and should not be a common name that might be used by other software. It should be in  `UPPERCASE`, with `UNDERSCORES_SEPARATING_WORDS`. It should be descriptive, and should not be an abbreviation unless the abbreviation is widely understood.

* Add the new env var to the **non-committed** `envs/.env` file. This file should be used to set the environment variables for your local development. **This file should not be committed to the repository**. You can use real values for the environment variables in this file. **Group related ENVs together** in this file, following the style of the `env-template` file.

* Add the new env var to the `envs/env-template` file, which is the ONLY file in the /envs/ folder that should be committed to the repository. In this file you can set a **default/suggested value** for the variable (assuming that there is no security risk to disclosure of this), and add a **comment** to explain what it does. Commit and push this file to the repository. Group related env vars together in this file, keeping it the same order as the `.env` file.

* Usually the env var's value will be accessed somewhere in `settings.py` with something like `os.getenv("ENV_VAR_NAME")`. Try to keep the env var name consistent with the variable name used in the code. Also aim to **group related settings together** in the settings file. Comments here are useful in knowing what the variable does and aid maintainability.

* Make the env var available to GitHub Actions and the deployment environments. See below for details.

### Pushing the env vars to GitHub for Actions to use it

There is a script in the `s/` folder which uses the `gh` GitHub CLI tool to push the contents of your `envs/.env` file as a base64-encoded string to a *single* GitHub secret called ENVIRONMENT in the E12 repository. This is then used by the GitHub Actions to decode and supply the appropriate env vars to the software stack during automated tests. You **can** safely push confidential information to this secret, as it is only accessible to the E12 repository.

### Pushing the env vars to our deployment environments

At present the env vars are manually copied into `/var/epilepsy12/envs/.env` in each of the deployment environments - Development, Staging and Live. This is done by the system admin over SSH. It is possible that in future we will use a more automated system for this.

### Sharing the env vars with other developers

All developers who have a local development environment will to need to be informed that there is a new env var, what an acceptable value fo it is, and what it does. One way to inform the team is using our secure Signal chat. Generally, confidential env var values are not shared by email or other insecure methods.

### Further documentation

Detailed documentation about the environment variable is **only** required if it not immediately clear from the name and comments that it does and how it is used.
