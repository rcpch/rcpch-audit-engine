---
title: Documentation
reviewers: Dr Marcus Baw
---

## Introduction

The RCPCH Audit Engine / Epilepsy12 documentation site is made with [Zensical](https://zensical.org/), a static site generator (built by the same team as Material for MkDocs) which takes Markdown source files from `documentation/docs` within the project and compiles them into a static HTML site. These static files are then served from our hosting resources.

## Docker development setup

As part of our standard Docker and Docker Compose development setup, we have a `docker-compose.yml` file in the root of the repo which will build a `zensical` Docker image with all the dependencies needed to run the documentation site locally.

You can view the documentation at `https://e12.localhost/docs`. Changes appear when the page is reloaded.

## How to edit content

* Generally any significant changes will need to be on a new Git branch, which by convention we name according to the 'slugified' title of the Issue that the changes resolve. Occasionally we will make small changes directly on the `development` branch, but this is not recommended.
* Make changes to the Markdown files in the `documentation/docs` folder.
* Ensure any new or renamed files are listed in the `nav` data structure within `mkdocs.yml` or they won't show up in the navigation.
* Save and review the auto-reloaded site on <https://localhost:8001>.
* Commit the changes. Try to keep commits tidy and 'atomic' - in that ideally a single commit should be one new or edited piece of content, not a whole raft of changes. This allows us to easily select which commits to include, and makes reviewing PRs easier.

## Reference guides

[Zensical](https://zensical.org/docs/) (the static site generator we are using, built by the Material for MkDocs team) has a host of features for making beautiful, practical, functional and easily navigable documentation.

### Markdown

Fundamental to the way the documentation works is the use of a simple set of text annotations called '[Markdown](https://daringfireball.net/projects/markdown/)', which are easily readable and editable as text files but can be compiled into HTML for web viewing. Markdown is hugely popular across the web for rapid entry of web-native formatted text, being the basis of much of GitHub, StackOverflow, and Discourse's functionality.

Markdown uses characters like asterisks (`*`), hashes (`#`) and others, to effect its formatting. For example: `**bold**` to denote **bold** text. It's simple to get used to and, once you're used to it, very productive too. One advantage is that formatted text *stays where it's been put*, unlike with some word processors in which the GUI formatting tools can have you chasing unpredictable and cascading formatting changes all over a document.

#### Online editing of Markdown

If you are new to Markdown editing, you can use GitHub's interface itself to edit in-browser, by clicking the 'pencil' edit icon in the top right corner of any source code page. There are also external tools like [Prose.io](http://prose.io/) and [StackEdit](https://stackedit.io/) which give you a nice interface for editing Markdown in a browser, and will sync the changes with GitHub for you.

If Markdown seems daunting then another option is simply to edit the content in the word processor of your choice and then ask one of the RCPCH Developer team to convert it to Markdown and add it to the documentation.

### Pymdownx extensions

Some of the features such as [Keys](https://squidfunk.github.io/mkdocs-material/setup/extensions/python-markdown-extensions/#keys) come from extensions like [Pymdownx](https://facelessuser.github.io/pymdown-extensions/extensions/arithmatex/)

## Pull requests (no commit rights)

If you are not a member of the RCPCH Developer team, you many not have commit rights to the documentation repository, so to publish your changes you will need to submit a pull request. This is a standard GitHub process, but if you are not familiar with it, here are the steps:

* Push your changes to a branch on **your** fork of the repository.
* The branch should ideally be name according to the feature or fix it includes.
* Go to your fork of the repository on GitHub and click the 'Pull Request' button.
* Submit a pull request from your fork to the **`development`** branch of the main repository.

## Deployment (for RCPCH Developer team)

See [Deployment](./deployment.md) for details of how the documentation site is deployed.

## NOT RECOMMENDED: Setting up a Python and Pyenv development environment for the E12 documentation site

!!! warning "Use the Dockerised development environment if you can"
    If you cannot use the Dockerised development environment, then you will need to set up a Python environment on your local machine to run the documentation site locally. We highly recommend using the Dockerised development environment if you can, as it is much easier to set up and use.

Create a virtualenv for the Python modules:

* Install `pyenv` using the instructions at <https://github.com/pyenv/pyenv-installer>
* Any recent Python version works, we tend to use 3.11
* Calling it `zensical` will enable Pyenv to automatically select it when you navigate to the directory, because this will match the contents of the `.python-version` file in the root of the project.

```console
pyenv virtualenv 3.11 zensical
```

The first time you want to use the `zensical` pyenv, you will need to activate it. Subsequent times it should automatically be activated if you have named it the same as the entry in the `.python-version` file in the root of the project.

```console
pyenv activate zensical
```

### Install Zensical

Install all the Python requirements

```console
pip install -r requirements.txt
```

### Running the development Zensical server

`zensical serve` starts up a development server which will auto-reload after changes to the source files, and will serve the documentation on [`localhost:8001`](http://localhost:8001).

To run `zensical serve` the fastest way, use

```console
zensical serve
```

`mkdocs.yml` lives at the root of the project, so Zensical auto-discovers it. Run the command from the root of the project.
