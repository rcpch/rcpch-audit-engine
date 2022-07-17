---
title: Development
reviewers: Dr Marcus Baw
---

## Getting started

The RCPCH Audit Engine Epilepsy 12 platform

## Documentation development

The RCPCH Audit Engine / Epilepsy 12 documentation is made with Material for MkDocs.

This is a framework, separate from Django, which takes Markdown source files from `docs` and compiles them into a static site which is built to `staticfiles/docs-site`. These static files are then served by Django as part of the rest of the app. It means we can use all the niceness of MkDocs and the Material theme, and yet it all appears within the main Django site.

### Setup

You need to have Material for MkDocs installed (this installs MkDocs as well for you)

In most circumstances this is simply `pip install mkdocs-material`, but if you hit issues then there is more information at https://squidfunk.github.io/mkdocs-material/getting-started/

There are two ways to develop using MkDocs in our project:

#### 1. **`mkdocs serve`**  
One way is to run `mkdocs serve`, which starts up a development server which will auto-reload after changes to the source files, and will serve the documentation on [`localhost:8001`](http://localhost:8001). This is useful for when you are making lots of changes or doing a big edit. You'll be viewing the documentation site in a different tab to the Audit Engine, and the changes won't be visible in Audit Engine until you run `mkdocs build`.
   
!!! important
    In order to test the final documentation edits, you **MUST** run `mkdocs build` at the end of your edits. Then use option 2 below to test the docs 'in situ' within the Django site.

#### 2. **`mkdocs build`**  
The other way is to make your changes and then periodically run `mkdocs build`, which builds the site into the `staticfiles/docs-site` directory. If you are running the Django app in development then the new docs will be at [`http://0.0.0.0:8000/epilepsy12/docs/`](http://0.0.0.0:8000/epilepsy12/docs/), and accessible through the navigation as part of the main Django app.

### Editing content

* Check out a new local branch on which to make the changes, with a descriptive name.
* Make changes to the Markdown files in the `docs` folder in the project root.
* Save the changes.
* If you're using `mkdocs serve` then the auto-reloaded site will show the changes.
* If not, then run `mkdocs build` and view the changes in the Django site.
* Commit the changes. Try to keep commits tidy and 'atomic' - in that ideally a single commit should be one new or edited piece of content, not a whole raft of changes. This allows us to easily select which commits to include.
* Push the changes and create a pull request to have them included in the main project.
