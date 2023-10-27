---
title: Code Style
reviewers: Dr Marcus Baw
---

## IDE / Text Editor

We recommend the use of the popular [VSCode](https://code.visualstudio.com/) editor, which has rapidly become the most popular editor in the last few years. It has good support for Python and Django, and additional features such as LiveShare and Azure integration are also helpful.

The below instructions regarding linting and formatting assume the use of VSCode

## Linter

We use the PyLint linter. It promotes consistency if all of the team use the same linting and formatting rules.

You may need to install the `pylint_django` plugin and add `--load-plugins=pylint_django` to the PyLintArgs:

- Press ++ctrl+comma++ to enter VSCode's Settings

- Search for `python linting` and scroll down to PyLint
- Ensure `Python > Linting: Pylint Enabled` is checked

- In `Python > Linting: Pylint Path` write `pylint_django`

- In `Python > Linting Pylint Args` add `--load-plugins=pylint_django`

## Formatter

## Imports

Python imports should be categorised:

```python
# standard imports

# third party imports

# RCPCH imports
```

In addition, both packages and individual functions/classes should be listed alphabetically.

All of the above measures help to prevent duplicates, ensures tidiness and maintainability, and lets us see easily which of our imports are most reliable and trusted.
