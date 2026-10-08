"""Capture a CI command's diagnostics without masking its exit code."""

import os
import subprocess
import sys
from pathlib import Path

report = Path(sys.argv[1])
command = sys.argv[2:]
if command[0] == "python":
    command[0] = sys.executable
result = subprocess.run(
    command,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding="utf-8",
    errors="replace",
)
print(result.stdout)
report.write_text(result.stdout, encoding="utf-8")
if os.environ.get("GITHUB_STEP_SUMMARY"):
    with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as summary:
        summary.write(f"\n## {report.stem}\n\n```text\n{result.stdout[-40000:]}\n```\n")
sys.exit(result.returncode)
