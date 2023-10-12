---
title: Documentation
reviewers: Dr Marcus Baw
---

## Introduction

The RCPCH Audit Engine / Epilepsy12 documentation site is made with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/), which is a framework, separate from Django, which takes Markdown source files from `docs` and compiles them into a static HTML site. These static files are then served from our hosting resources.

## Docker development setup

As part of our standard Docker and Docker Compose development setup, we have a `docker-compose.yml` file in the root of the repo which will build a `mkdocs` Docker image with all the dependencies needed to run the documentation site locally.

By default this image is running in a container at `localhost:8001` when you run the Docker dev setup using `s/docker-up` and it will auto-reload when you make changes to the source files in `documentation/docs`.

## How to edit content

* Check out a **new local branch** on which to make the changes, with a **descriptive name**.
* Make changes to the Markdown files in the `documentation/docs` folder.
* Ensure any new or renamed files are listed in the `nav` element within `mkdocs.yml` or they won't show up.
* Save and the changes.
* The auto-reloaded site will show the changes.
* Commit the changes. Try to keep commits tidy and 'atomic' - in that ideally a single commit should be one new or edited piece of content, not a whole raft of changes. This allows us to easily select which commits to include.

## Reference guides

*MkDocs* and *Material for MkDocs* (the MkDocs theme we are using) have a host of features for making beautiful, practical, functional and easily navigable documentation.

### Markdown

Fundamental to the way the documentation works is the use of a simple set of text annotations called '[Markdown](https://daringfireball.net/projects/markdown/)', which are easily readable and editable as text files but can be compiled into HTML for web viewing. Markdown is hugely popular across the web for rapid entry of web-native formatted text, being the basis of much of GitHub, StackOverflow, and Discourse's functionality.

Markdown uses characters like asterisks (`*`), hashes (`#`) and others, to effect its formatting. For example: `**bold**` to denote **bold** text. It's simple to get used to and, once you're used to it, very productive too. One advantage is that formatted text stays where it's been put, unlike with some word processors in which the GUI formatting tools can have you chansing formatting changes all over a document.

#### Online editing of Markdown

If you are new to Markdown editing, you can use GitHub's interface itself to edit online, by clicking the 'pencil' edit icon in the top right corner of any source code page. There are also external tools like [Prose.io](http://prose.io/) and [StackEdit](https://stackedit.io/) which give you a nice interface for editing Markdown online, and will sync the changes with GitHub for you.

If Markdown seems daunting then another option is simply to edit the content in the word processor of your choice and then ask one of the RCPCH Incubator team to convert it to Markdown and add it to the documentation.

### Material for MkDocs

On top of the basic features of Markdown, MkDocs and the *Material for MkDocs* theme together add all the nice website appearance and many additional features for making beautiful documentation sites.

A good overview can be had from looking at the [Material for MkDocs Reference section](https://squidfunk.github.io/mkdocs-material/reference/) and from copying existing code in our documentation that does what you need.

### MkDocs

If you can't find functionality documented in the Material for MkDocs theme website, this is usually because it is functionality which comes from MkDocs, the underlying framework, itself. See the [MkDocs](https://www.mkdocs.org/user-guide/writing-your-docs/#writing-with-markdown) site for these features.

### Pymdownx extensions

Some of the features such as [Keys](https://squidfunk.github.io/mkdocs-material/setup/extensions/python-markdown-extensions/#keys) come from extensions like [Pymdownx](https://facelessuser.github.io/pymdown-extensions/extensions/arithmatex/)

## Pull requests (no commit rights)

If you are not a member of the RCPCH Incubator team, you many not have commit rights to the documentation repository, so to publish your changes you will need to submit a pull request. This is a standard GitHub process, but if you are not familiar with it, here are the steps:

* Push your changes to a branch on **your** fork of the repository.
* The branch should ideally be name according to the feature or fix it includes.
* Go to your fork of the repository on GitHub and click the 'Pull Request' button.
* Submit a pull request from your fork to the **`development`** branch of the main repository.

## Deployment (for RCPCH Incubator team)

When a push is made to either the `prerelease` or `live` branches, or a pull request is made against `prerelease`, the site is built and deployed to Azure automatically. (Builds are not triggered for PRs against `live` as this branch is often used by RCPCH staff making small PRs to update the documentation, and the build errors due to lack of GitHub access token were causing unnecessary confusion)

* Prerelease URL <https://witty-bush-03ee83f03-prerelease.westeurope.1.azurestaticapps.net>
* Live URL <https://epilepsy12docs.rcpch.tech>
* URLs for PRs against `prerelease` are added to the PR comments automatically by Azure

## NOT RECOMMENDED: Setting up a Python and Pyenv development environment for the E12 documentation site

!!! warning "Use the Dockerised development environment if you can"
    If you cannot use the Dockerised development environment, then you will need to set up a Python environment on your local machine to run the documentation site locally. We highly recommend using the Dockerised development environment if you can, as it is much easier to set up and use.

Create a virtualenv for the Python modules:

* For info on setting up Pyenv see [Python setup](../api-python.md)
* Any recent Python version works, we tend to use 3.11
* Calling it `mkdocs` will enable Pyenv to automatically select it when you navigate to the directory, because this will match the contents of the `.python-version` file in the root of the project.

```console
pyenv virtualenv 3.11 mkdocs
```

The first time you want to use the `mkdocs` pyenv, you will need to activate it. Subsequent times it should automatically be activated if you have named it the same as the entry in the `.python-version` file in the root of the project.

```console
pyenv activate mkdocs
```

### Install Material for Mkdocs

Install all the Python requirements

```console
pip install -r requirements.txt
```

### Running the development MkDocs server

`mkdocs serve` starts up a development server which will auto-reload after changes to the source files, and will serve the documentation on [`localhost:8001`](http://localhost:8001).

To run `mkdocs serve` the fastest way, use

```console
export ENABLE_PDF_EXPORT=0;mkdocs serve  --config-file documentation/mkdocs.yml
```

`ENABLE_PDF_EXPORT=0 disables the generation of the PDF version of the documentation, which is slow and not needed in development.
`--config-file documentation/mkdocs.yml` tells MkDocs to use the `mkdocs.yml` file in the `documentation` folder. This assumes that you are running the command from the root of the project.

If you want the automatic PDF generation to happen in development locally, then run

```console
export ENABLE_PDF_EXPORT=1;mkdocs serve  --config-file documentation/mkdocs.yml
```

The PDF generation slows down the hot reloading by about 10-15 seconds so it can get tiresome in development. PDF generation will automatically happen in production when the site is built and deployed, even if you didn't generate PDFs in local development.
