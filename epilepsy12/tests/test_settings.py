import os
from pathlib import Path
import subprocess
import sys


def test_production_settings_require_django_secret_key(tmp_path):
    environment = os.environ.copy()
    environment.pop("DJANGO_SECRET_KEY", None)
    environment["DEBUG"] = "False"
    environment["PYTHONPATH"] = os.pathsep.join(
        filter(None, (str(Path.cwd()), environment.get("PYTHONPATH")))
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import importlib; importlib.import_module('rcpch-audit-engine.settings')",
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "DJANGO_SECRET_KEY must be set when DEBUG is False." in result.stderr
