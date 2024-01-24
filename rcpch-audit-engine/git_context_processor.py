"""
This module contains a function to get the active branch and latest commit hash
from the git repo.
"""

from pathlib import Path
import logging

# set up logging
logger = logging.getLogger(__name__)


def get_active_branch_and_commit(_request):
    """
    Gets the active branch and latest commit hash from the git repo
    """

    # set defaults/fallback for values in git_data dict
    git_data = {
        "active_git_branch": "[branch name not found]",
        "latest_git_commit": "[latest commit hash not found]",
    }

    head_dir = Path(".") / ".git" / "HEAD"
    with head_dir.open("r") as f:
        head_branch = f.read().splitlines()
    for line in head_branch:
        if line[0:4] == "ref:":
            git_data["active_git_branch"] = line.partition("refs/heads/")[2]
    logger.info("Active git branch: %s", git_data["active_git_branch"])

    refs_dir = Path(".") / ".git" / "refs" / "heads" / git_data["active_git_branch"]
    with refs_dir.open("r") as f:
        git_data["latest_git_commit"] = f.read().splitlines()[0]
    logger.info("Latest git commit: %s", git_data["latest_git_commit"])

    return git_data
