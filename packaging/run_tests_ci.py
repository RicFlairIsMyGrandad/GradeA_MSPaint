"""Keep the real pytest status and expose a readable Windows test report."""

import os
import subprocess
import sys
from pathlib import Path

result = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "--tb=short"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding="utf-8",
    errors="replace",
)
print(result.stdout)
Path("windows-tests.txt").write_text(result.stdout, encoding="utf-8")
if os.environ.get("GITHUB_STEP_SUMMARY"):
    Path(os.environ["GITHUB_STEP_SUMMARY"]).write_text(
        "## Windows test results\n\n```text\n" + result.stdout + "\n```\n",
        encoding="utf-8",
    )
sys.exit(result.returncode)
