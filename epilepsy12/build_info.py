import os
import json
import subprocess
import logging


logger = logging.getLogger(__name__)
_build_info = None

def get_build_info_from_dot_git_folder():
    try:
        result = subprocess.run('s/get-build-info', stdout = subprocess.PIPE)
        return json.loads(result.stdout)
    except:
        logger.exception("Error getting git data from repository")
        return {
            "active_git_branch": "[branch name not found]",
            "latest_git_commit": "[latest commit hash not found]",
        }

def get_build_info(request=None):
    global _build_info
    
    if not _build_info:
        try:
            with open("build_info.json", "r") as f:
                _build_info = json.load(f)
        except:
            # Running in dev
            _build_info = get_build_info_from_dot_git_folder()
    
    return _build_info
