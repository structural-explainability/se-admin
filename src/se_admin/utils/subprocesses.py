"""utils/subprocesses.py.

Utility functions for running subprocesses, e.g. git commands, gh commands, etc.
"""

from pathlib import Path
import subprocess

# === Run Command ===


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a shell command in the given directory, returning the completed process."""
    if not command or not all(isinstance(arg, str) for arg in command):
        raise ValueError("command must be a non-empty list of strings")
    return subprocess.run(  # noqa: S603, S607
        command,
        cwd=cwd,
        check=False,
        text=True,
        capture_output=True,
        shell=False,
    )
