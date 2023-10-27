from pathlib import Path


def get_active_branch_and_commit(request):
    """
    Gets the `GIT_HASH` environment variable, created in GitHub Actions workflow, inserts into all templates.
    
    If there is no git_hash.txt, such as in local dev, looks directly in the .git folder.
    """
    # Load the txt file containing hash
    try:
        with open("git_hash.txt", "r") as f:
            git_branch, git_hash = f.read().split(",")

            latest_git_commit = git_hash.replace("GIT_HASH=", "")
            active_git_branch = git_branch.replace("GIT_BRANCH=", "")

    except FileNotFoundError:
        try:
            head_dir = Path(".") / ".git" / "HEAD"
            with head_dir.open("r") as f:
                head_branch = f.read().splitlines()
            for line in head_branch:
                if line[0:4] == "ref:":
                    active_git_branch = line.partition("refs/heads/")[2]
        except:
            active_git_branch = "[branch name not found]"

        try:
            refs_dir = Path(".") / ".git" / "refs" / "heads" / active_git_branch
            with refs_dir.open("r") as f:
                latest_git_commit = f.read().splitlines()[0]

        except:
            latest_git_commit = "[latest commit hash not found]"

    admin_data = {
        "latest_git_commit": latest_git_commit,
        "active_git_branch": active_git_branch,
    }

    return admin_data
